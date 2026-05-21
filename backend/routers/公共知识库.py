


from fastapi import APIRouter, Request, Body, HTTPException
from concurrent.futures import ThreadPoolExecutor
from core.sqlLiteExec import sqlite_execute
import hashlib
import base64
import os
import shutil
import json
from datetime import datetime
from typing import Optional, List, Union

executor = ThreadPoolExecutor()
router = APIRouter(
    prefix="/public_knowledgebase",
    tags=["公共知识库相关的操作接口"],
)


def _ensure_public_file_hash_schema() -> None:
    """为 publicDatabase_file 增加 content_hash，并建 (category_id, content_hash) 索引；查重用一条 SQL，不靠遍历。"""
    info = sqlite_execute("PRAGMA table_info(publicDatabase_file)")
    if not info:
        return
    names = {row["name"] for row in info}
    if "content_hash" not in names:
        sqlite_execute(
            "ALTER TABLE publicDatabase_file ADD COLUMN content_hash TEXT",
            fetch="none",
        )
    sqlite_execute(
        "CREATE INDEX IF NOT EXISTS idx_publicDatabase_file_category_content_hash "
        "ON publicDatabase_file(category_id, content_hash)",
        fetch="none",
    )



def _run_in_threadpool(func, *args):
    """后台线程执行，不阻塞 FastAPI 主循环。"""
    return executor.submit(func, *args)


# =======公共知识库=======
# 上传一个文件的信息，执行上传
@router.post("/upload_file", summary="上传单个文件")
async def upload_file(
        request: Request,
        user_id: int = Body(..., embed=True, description="操作用户id"),
        category_id: int = Body(..., embed=True, description="目标目录 id，必须存在于 publicDatabase_categories"),
        filename: str = Body(..., embed=True, description="原始文件名，含扩展名，如 report.pdf"),
        base64_data: str = Body(..., embed=True, description="文件内容 Base64 字符串，不含 data:xxx;base64, 前缀"),
        title: str = Body(..., embed=True, description="文档标题"),
        description: Optional[str] = Body(None, embed=True, description="文档描述"),
        tags: Optional[list[str]] = Body(None, embed=True, description="标签列表，如 ['钻井','深井']"),
):
    # 0. 权限校验，判断用户是否拥有上传权限
    perm_check_sql = """
        SELECT permission
        FROM user_permissions
        WHERE user_id = ? AND permission = 'public_db_document:upload'
    """
    perm_result = sqlite_execute(perm_check_sql, (user_id,))
    if not perm_result:
        raise HTTPException(status_code=403, detail="您没有权限上传公共知识库文件")

    title_clean = (title or "").strip()
    if not title_clean:
        raise HTTPException(status_code=400, detail="文档标题不能为空")

    # ── Base64 解码（先解码再按内容判重）────────────────────────
    try:
        file_bytes = base64.b64decode(base64_data)
    except Exception:
        raise HTTPException(status_code=400, detail="base64_data 解码失败，请确认字符串合法且不含 data: 前缀")

    content_hash = hashlib.sha256(file_bytes).hexdigest()
    _ensure_public_file_hash_schema()
    dup = sqlite_execute(
        "SELECT id FROM publicDatabase_file WHERE category_id=? AND content_hash=?",
        (category_id, content_hash),
    )
    if dup:
        raise HTTPException(
            status_code=409,
            detail="该分类下已存在相同内容的文件，未重复上传。",
        )

    # ── 提取文件类型 ───────────────────────────────────────────
    _, ext = os.path.splitext(filename)
    file_type = ext.lstrip(".").lower()  # 如 "pdf" / "docx"
    file_size = len(file_bytes)

    # ── 先插入数据库获取专属目录知识 ID ───────────────────
    tags_json = json.dumps(tags, ensure_ascii=False) if tags else None
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        sqlite_execute(
            """
            INSERT INTO publicDatabase_file
                (category_id, title, file_path, file_type, file_size, description, tags, created_at, updated_at, content_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (category_id, title_clean, "", file_type, file_size, description, tags_json, now, now, content_hash),
        )
        # 因为 sqlite_execute 每次都会新建数据库连接，last_insert_rowid() 会失效并返回 0
        # 所以我们通过刚才插入的 category_id 和唯一的 content_hash 来反查获取刚插入记录的 ID
        new_id_res = sqlite_execute(
            "SELECT id FROM publicDatabase_file WHERE category_id=? AND content_hash=?",
            (category_id, content_hash)
        )
        new_id = new_id_res[0]["id"] if new_id_res else 0
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库初始记录写入失败: {e}")

    # ── 写入磁盘 ───────────────────────────────────────────────
    UPLOAD_ROOT = "./file_data/public_db"
    save_dir = os.path.join(UPLOAD_ROOT, str(new_id))
    os.makedirs(save_dir, exist_ok=True)

    abs_path = os.path.join(save_dir, filename)
    rel_path = f"public_db/{new_id}/{filename}"

    try:
        with open(abs_path, "wb") as f:
            f.write(file_bytes)
    except Exception as e:
        sqlite_execute("DELETE FROM publicDatabase_file WHERE id=?", (new_id,))
        raise HTTPException(status_code=500, detail=f"文件写入失败: {e}")

    # ── 同步更新地址和 RAGFlow ─────────────────────────────────
    try:
        sqlite_execute("UPDATE publicDatabase_file SET file_path=? WHERE id=?", (rel_path, new_id))

        # ── 调用 RAGFlow 上传 ───────────────────────────────────────
        try:
            from services.ragflow_service import upload_to_ragflow, start_parsing_document
            ragflow_result = upload_to_ragflow(abs_path)
            print(f"RAGFlow 上传结果: {ragflow_result}")

            # 解析刚才上传的文件的 ID，并立刻触发解析嵌入
            if ragflow_result and ragflow_result.get("code") == 0 and ragflow_result.get("data"):
                document_id = ragflow_result["data"][0]["id"]
                parse_result = start_parsing_document([document_id])
                print(f"RAGFlow 触发解析结果: {parse_result}")

                # 尝试更新 ragflow_id
                sqlite_execute("UPDATE publicDatabase_file SET ragflow_id=? WHERE id=?", (document_id, new_id))

        except Exception as e:
            # RAGFlow 失败不阻断写入，但记录错误
            print(f"RAGFlow 调用失败（不阻断写入）: {e}")

    except Exception as e:
        # 数据库写入失败时回滚已落盘的文件
        import shutil
        if os.path.exists(save_dir):
            shutil.rmtree(save_dir)
        sqlite_execute("DELETE FROM publicDatabase_file WHERE id=?", (new_id,))
        raise HTTPException(status_code=500, detail=f"文件上传处理失败: {e}")

    return {
        "success": True,
        "data": {
            "id": new_id,
            "category_id": category_id,
            "title": title_clean,
            "filename": filename,
            "file_path": rel_path,
            "file_type": file_type,
            "file_size": file_size,
        },
    }


# 获取当前公共知识库结构
@router.post("/get_structure")
async def get_structure(request: Request, user_id: Optional[int] = Body(None, embed=True, description="操作用户id")):
    # 优先从 body 获取，否则尝试从 cookie 中获取
    if not user_id:
        cookie_uid = request.cookies.get("user_id")
        if cookie_uid and cookie_uid.isdigit():
            user_id = int(cookie_uid)

    res = sqlite_execute("SELECT * FROM `publicDatabase_categories`")
    
    if user_id:
        perm_sql = """
            SELECT permission
            FROM user_permissions
            WHERE user_id = ? AND permission LIKE 'public_db_document_browse:%'
        """
        perm_result = sqlite_execute(perm_sql, (user_id,))
        print("权限结果:", perm_result)
        # 如果配置了此权限，进行过滤
        if perm_result:
            allowed_root_ids = []
            import re
            for row in perm_result:
                perm_str = row.get('permission', '')
                # 正则提取方括号内的所有数字
                match = re.search(r'\[(.*?)\]', perm_str)
                if match:
                    nums = re.findall(r'\d+', match.group(1))
                    allowed_root_ids.extend([int(x) for x in nums])
                    
            if allowed_root_ids:
                filtered_res = []
                for item in res:
                    item_id = item.get('id')
                    path = item.get('path') or ''
                    
                    # 当前节点本身在允许列表中，或是允许节点的子孙节点（通过 path 中是否包含 /id/ 判断）
                    if item_id in allowed_root_ids or any(f"/{root_id}/" in path for root_id in allowed_root_ids):
                        filtered_res.append(item)
                        
                res = filtered_res
            else:
                res = []
        else:
            # 没有相关权限记录，视业务需要可能返回空（如果没有赋权就不让看）
            res = []
    else:
        # 未传入且未获取到用户信息时拦截
        return {"code": 403, "msg": "缺少用户信息，无权限访问", "data": []}

    return {"code": 200, "msg": 'success', "data": res}


# 获取当前公共知识库某个目录下的文件
@router.post("/get_files_by_category_id")
async def get_files_by_category_id(request: Request, category_id: int = Body(..., embed=True, description="目录id")):
    res = sqlite_execute("SELECT * FROM `publicDatabase_file` WHERE category_id=?", (category_id,))
    return {"code": 200, "msg": 'success', "data": res}


# 获取某个文件的详细信息，包括全部信息+base64，包括其完整的分类路径
@router.post("/get_public_file_by_id")
async def get_public_file_by_id(request: Request, file_id: int = Body(..., embed=True, description="文件id")):
    res = sqlite_execute("SELECT * FROM `publicDatabase_file` WHERE id=?", (file_id,))
    if not res:
        return {"code": 404, "msg": "文件不存在", "data": None}

    # 根据 res 中包含的路径，将其转为 base64
    file_path_str = res[0]['file_path']
    if file_path_str:
        file_path = f"./file_data/{file_path_str}"
        # 使用 os.path.isfile 验证路径是否真的对应一个文件，防止把目录（比如 ./file_data/）当成文件来打开
        if os.path.isfile(file_path):
            try:
                with open(file_path, "rb") as f:
                    file_base64 = base64.b64encode(f.read()).decode("utf-8")
                res[0]['file_base64'] = file_base64
            except Exception as e:
                print(f"读取文件失败: {e}")
                res[0]['file_base64'] = None
        else:
            print(f"读取文件失败: 目标不是文件或不存在 ({file_path})")
            res[0]['file_base64'] = None
    else:
        res[0]['file_base64'] = None

    # 获取完整的分类路径，需要循环处理，直至其parent_id为null
    category_path = []
    category_id = res[0]['category_id']
    while category_id:
        category = sqlite_execute("SELECT * FROM `publicDatabase_categories` WHERE id=?", (category_id,))
        if not category:
            break
        category_path.append(category[0]['name'])
        category_id = category[0]['parent_id']
    category_path.reverse()
    res[0]['category_path'] = category_path

    return {"code": 200, "msg": 'success', "data": res}


# 查找关键字，从知识库查找文件名称中有这个内容的数据，返回目录id
@router.post("/search_keyword")
async def search_keyword(request: Request, keyword: str = Body(..., embed=True, description="关键字")):
    res = sqlite_execute("SELECT * FROM `publicDatabase_file` WHERE title LIKE ?", (f"%{keyword}%"))
    return {"code": 200, "msg": 'success', "data": res}


# 删除公共知识库文件
@router.post("/delete_public_file_by_id")
async def delete_public_file_by_id(
        request: Request,
        file_id: int = Body(..., embed=True, description="文件id"),
        user_id: int = Body(..., embed=True, description="操作用户id")
):
    # 0. 权限校验，判断用户是否拥有删除权限
    perm_check_sql = """
        SELECT permission
        FROM user_permissions
        WHERE user_id = ? AND permission = 'public_db_document:delete'
    """
    perm_result = sqlite_execute(perm_check_sql, (user_id,))
    if not perm_result:
        return {"code": 403, "msg": "您没有权限删除公共知识库文件", "data": None}

    # 1. 查询文件记录以获取文件存储的相对路径供删除
    file_info = sqlite_execute("SELECT * FROM `publicDatabase_file` WHERE id=?", (file_id,))

    if file_info:
        file_path = f"./file_data/{file_info[0]['file_path']}"
        try:
            import shutil
            file_dir = os.path.dirname(file_path)
            if os.path.exists(file_dir) and file_dir != "./file_data/public_db":
                shutil.rmtree(file_dir)
                print(f"公共知识库文件及其专属目录已从本地服务器删除: {file_dir}")
            elif os.path.exists(file_path):
                os.remove(file_path)
                print(f"公共知识库文件已从本地服务器删除: {file_path}")
        except Exception as e:
            print(f"删除物理目录或文件阶段发生错误: {e}")

    # 2. 从数据库删除关联记录
    res = sqlite_execute("DELETE FROM `publicDatabase_file` WHERE id=?", (file_id,))

    # 3. 从ragflow中删除文件
    try:
        file_id = file_info[0]['ragflow_id']
        from services.ragflow_service import delete_file_from_ragflow
        print(delete_file_from_ragflow(file_id))
    except Exception as e:
        print(f"从ragflow中删除文件失败: {e}")

    return {"code": 200, "msg": 'success', "data": res}







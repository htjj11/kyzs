'''
从数据库获取知识接口
'''
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List
import uuid
import json
from datetime import datetime

from fastapi import APIRouter, Request, Body, HTTPException
from services.literature_service import siliconflow_deepseek_answer
from core.utils import extract_json
from core.sqlLiteExec import sqlite_execute
import base64
import hashlib
import os
import requests
executor = ThreadPoolExecutor()


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

router = APIRouter(
    prefix="/get_knowledge",
    tags=["与知识库相关的操作接口"],
)

#=======个人知识库======

#获取当前用户id下全部知识库内容
@router.post("/get_all_knowledge")
async def get_all_label(
    request: Request,
    user_id: int = Body(..., embed=True, description="用户id")
):
    res = sqlite_execute("SELECT * FROM `knowledgebase` WHERE user_id=?", (user_id,))

    for item in res:
        label_result = sqlite_execute(
            "SELECT label_name FROM `label` WHERE id=?", (item['label_id'],)
        )
        item['label_name'] = label_result[0]['label_name'] if label_result else '未定义'

    return {"code": 200, "msg": 'success', "data": res}

#删除知识库内容
@router.post("/delete_knowledge_by_id")
async def delete_knowledge_by_id(
    request: Request,
    knowledge_id: int = Body(..., embed=True, description="知识id")
):
    print(f'用户请求删除知识库内容：{knowledge_id}')
    #判断type_id是否为5，如果是且mark_info可以被解析为json，则删除文件  
    knowledge_info = sqlite_execute("SELECT * FROM `knowledgebase` WHERE id=?", (knowledge_id,))
    if knowledge_info[0]['type_id'] == 5:
        #如果knowledge_info的mark_info中包含original_filename字符串，则表示他是一个文件
        if 'original_filename' in knowledge_info[0]['mark_info']:
            file_name = eval(knowledge_info[0]['mark_info'])['filename']
            file_path = f"file_data/{file_name}"
            try:
                os.remove(file_path)
            except Exception as e:
                print(f'删除文件失败：{e}')
    res = sqlite_execute("DELETE FROM `knowledgebase` WHERE id=?", (knowledge_id,))
    return {"code": 200, "msg": 'success', "data": res}

#更新知识库内容
@router.post("/update_knoledge_by_id")
async def update_knoledge_by_id(
    request: Request,
    knowledge_id: int = Body(..., embed=True, description="知识id"),
    knowledge_title: str = Body(..., embed=True, description="知识名称"),
    knowledge_content: str = Body(..., embed=True, description="知识内容"),
    knowledge_label: int = Body(..., embed=True, description="知识标签id"),
    knowledge_type: int = Body(..., embed=True, description="知识类型"),
    knowledge_mark_info: str = Body(..., embed=True, description="知识来源")
):
    res = sqlite_execute(
        """UPDATE `knowledgebase`
           SET title=?, content=?, label_id=?, type_id=?, mark_info=?
           WHERE id=?""",
        (knowledge_title, knowledge_content, knowledge_label, knowledge_type, knowledge_mark_info, knowledge_id)
    )
    return {"code": 200, "msg": 'success', "data": res}

#根据知识库内容生成AI回复，用于改写、润色等
@router.post("/generate_content_by_ai")
async def generate_content_by_ai(
    request: Request,
    knowledge_content: str = Body(..., embed=True, description="知识内容"),
    prompt: str = Body(..., embed=True, description="提示词")
):
    full_prompt = (
        "请根据以下内容，生成符合提示词要求的内容：\n"
        f"原始内容：{knowledge_content}\n"
        f"用户需求提示词：{prompt}\n"
        r"返回的生成内容请以json格式返回，格式为{content:'生成的内容'}"
    )
    print('用户请求生成AI回复:', full_prompt)

    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(executor, siliconflow_deepseek_answer, full_prompt)

    data = extract_json(res)
    return {"code": 200, "msg": 'success', "data": data}


#传入文件存储名称，返回file_data路径下文件base64供用户下载
@router.post("/get_file_by_id")

async def get_file_by_id(
    request: Request,
    file_name: str = Body(..., embed=True, description="文件名")
):
    print(f'用户请求获取文件：{file_name}')
    # 从file_data目录中找出文件名对应的文件，并返回base64
    file_path = f"file_data/{file_name}"
    try:
        with open(file_path, "rb") as f:
            file_base64 = base64.b64encode(f.read()).decode("utf-8")
        return {"code": 200, "msg": 'success', "data": file_base64}
    except Exception as e:
        print(f'用户请求获取文件失败：{e}')
        return {"code": 500, "msg": 'error', "data": str(e)}


#将个人知识库的内容转移到公共知识库接口
@router.post("/transfer_to_public", summary="将个人知识转为公共知识文件")
async def transfer_to_public(
    request: Request,
    user_id: int = Body(..., embed=True, description="操作用户id"),
    knowledge_id: int = Body(..., embed=True, description="个人知识库知识id"),
    category_id: int = Body(..., embed=True, description="公共知识库目标分类id")
):
    # 0. 权限校验，判断用户是否拥有 public_db_document:upload 上传权限
    perm_check_sql = """
        SELECT permission
        FROM user_permissions
        WHERE user_id = ? AND permission = 'public_db_document:upload'
    """
    perm_result = sqlite_execute(perm_check_sql, (user_id,))
    if not perm_result:
        raise HTTPException(status_code=403, detail="您没有权限操作公共知识库文件")

    # 1. 提取个人知识库信息
    knowledge_info = sqlite_execute("SELECT * FROM `knowledgebase` WHERE id=?", (knowledge_id,))
    if not knowledge_info:
        raise HTTPException(status_code=404, detail="未找到对应的个人知识记录")
    
    k_info = knowledge_info[0]
    
    import ast
    # 2. 获取文件存储地址与实际字节内容
    # 如果判断属于文件类型（type_id=5且存在original_filename）
    if k_info['type_id'] == 5 and 'original_filename' in k_info['mark_info']:
        try:
            mark_dict = ast.literal_eval(k_info['mark_info'])
            filename = mark_dict['filename'] # 在 file_data 下的存储名
            original_filename = mark_dict['original_filename'] # 用户看到的名字
        except Exception:
            raise HTTPException(status_code=400, detail="解析个人知识库文件信息失败")
        
        source_path = f"file_data/{filename}"
        if not os.path.exists(source_path):
            raise HTTPException(status_code=404, detail="个人知识库本地文件已丢失")
            
        with open(source_path, "rb") as f:
            file_bytes = f.read()
    else:
        # 如果是纯文本类型，直接将其内容转化为 txt 虚拟文件流做知识归档
        original_filename = f"{k_info.get('title', '未知纯文本知识')}.txt"
        file_bytes = k_info['content'].encode('utf-8')
        
    title_clean = k_info.get('title', original_filename).strip()
    
    # 3. 计算 Hash 查重
    content_hash = hashlib.sha256(file_bytes).hexdigest()
    _ensure_public_file_hash_schema()
    dup = sqlite_execute(
        "SELECT id FROM publicDatabase_file WHERE category_id=? AND content_hash=?",
        (category_id, content_hash),
    )
    if dup:
        raise HTTPException(status_code=409, detail="公共库该分类下已存在相同内容的文件，防重复上传。")
        
    # 4. 写入公共服务磁盘对应分类目录
    _, ext = os.path.splitext(original_filename)
    file_type = ext.lstrip(".").lower()
    file_size = len(file_bytes)
    
    UPLOAD_ROOT = "./file_data"
    save_dir = os.path.join(UPLOAD_ROOT, str(category_id))
    os.makedirs(save_dir, exist_ok=True)
 
    unique_name = f"{uuid.uuid4().hex}_{original_filename}"
    abs_path = os.path.join(save_dir, unique_name)
 
    try:
        with open(abs_path, "wb") as f:
            f.write(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"写入转移文件失败: {e}")
        
    # 5. 上传倒 RagFlow 并插入公共知识库数据库表
    rel_path = f"{category_id}/{unique_name}"
    description = ""
    tags_json = json.dumps([], ensure_ascii=False)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        from services.ragflow_service import upload_to_ragflow, start_parsing_document
        ragflow_result = upload_to_ragflow(abs_path)
        
        document_id = None
        if ragflow_result and ragflow_result.get("code") == 0 and ragflow_result.get("data"):
            document_id = ragflow_result["data"][0]["id"]
            start_parsing_document([document_id])
            
        sqlite_execute(
            """
            INSERT INTO publicDatabase_file
                (category_id, title, file_path, file_type, file_size, description, tags, created_at, updated_at, content_hash, ragflow_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (category_id, title_clean, rel_path, file_type, file_size, description, tags_json, now, now, content_hash, document_id),
        )
        new_id_res = sqlite_execute("SELECT last_insert_rowid() as id")
        new_id = new_id_res[0]["id"] if new_id_res else 0
        
    except Exception as e:
        if os.path.exists(abs_path):
            os.remove(abs_path)
        raise HTTPException(status_code=500, detail=f"RAGFlow 解析或数据库记录失败: {e}")
        
    return {
        "code": 200, 
        "msg": 'success',
        "data": {
            "id": new_id,
            "category_id": category_id,
            "title": title_clean,
            "filename": original_filename
        }
    }


#=======公共知识库======= 
#上传一个文件的信息，执行上传
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
    file_type = ext.lstrip(".").lower()   # 如 "pdf" / "docx"
    file_size = len(file_bytes)
 
    # ── 写入磁盘 ───────────────────────────────────────────────
    UPLOAD_ROOT = "./file_data"
    save_dir = os.path.join(UPLOAD_ROOT, str(category_id))
    os.makedirs(save_dir, exist_ok=True)
 
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    abs_path = os.path.join(save_dir, unique_name)
 
    try:
        with open(abs_path, "wb") as f:
            f.write(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件写入失败: {e}")
 
    # ── 写入数据库 ─────────────────────────────────────────────
    rel_path = f"{category_id}/{unique_name}"
    tags_json = json.dumps(tags, ensure_ascii=False) if tags else None
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 
    try:


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

                # 尝试插入文件记录
                sqlite_execute(
                    """
                    INSERT INTO publicDatabase_file
                        (category_id, title, file_path, file_type, file_size, description, tags, created_at, updated_at, content_hash,ragflow_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (category_id, title_clean, rel_path, file_type, file_size, description, tags_json, now, now, content_hash,document_id),
                )
                # 获取新插入的 ID
                new_id_res = sqlite_execute("SELECT last_insert_rowid() as id")
                new_id = new_id_res[0]["id"] if new_id_res else 0
                
        except Exception as e:
            # RAGFlow 失败不阻断写入，但记录错误
            print(f"RAGFlow 调用失败（不阻断写入）: {e}")



    except Exception as e:
        # 数据库写入失败时回滚已落盘的文件
        if os.path.exists(abs_path):
            os.remove(abs_path)
        raise HTTPException(status_code=500, detail=f"数据库写入失败: {e}")
 
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
 

#获取当前公共知识库结构
@router.post("/get_structure")
async def get_structure(request: Request):
    res = sqlite_execute("SELECT * FROM `publicDatabase_categories`")
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
    file_path = f"./file_data/{res[0]['file_path']}"
    try:
        with open(file_path, "rb") as f:
            file_base64 = base64.b64encode(f.read()).decode("utf-8")
        res[0]['file_base64'] = file_base64
    except Exception as e:
        print(f"读取文件失败: {e}")
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

#查找关键字，从知识库查找文件名称中有这个内容的数据，返回目录id
@router.post("/search_keyword")
async def search_keyword(request: Request, keyword: str = Body(..., embed=True, description="关键字")):
    res = sqlite_execute("SELECT * FROM `publicDatabase_file` WHERE title LIKE ?", (f"%{keyword}%"))
    return {"code": 200, "msg": 'success', "data": res}

#删除公共知识库一条消息
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
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"公共知识库文件已从本地服务器删除: {file_path}")
        except Exception as e:
            print(f"删除物理文件阶段发生错误: {e}")
            
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







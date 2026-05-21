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

from services.literature_service import add_article_to_knowledge, add_patent_to_knowledge, \
    add_online_infomation_to_knowledge, add_mycontent_to_knowledge,add_mycontent_file_to_knowledge

from services.第三方接口.大模型对话 import aiping_ai_answer
from core.utils import extract_json
from core.sqlLiteExec import sqlite_execute
import base64
import hashlib
import os
import re
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
    prefix="/personal_knowledgebase",
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

#增加内容到个人知识库
@router.post('/add_knowledge')
async def add_knowledge(
    request: Request,
    data_dict: dict = Body(..., embed=True, description="收藏信息"),
    label_id: int = Body(..., embed=True, description="收藏标签id"),
    user_id: int = Body(..., embed=True, description="用户id"),
    type_id: int = Body(..., embed=True, description="收藏类型(1是文献；2专利；3网络信息；4自定义信息)"),
):
    """
    添加收藏接口，将收藏信息添加到数据库中，现判定type属于哪一类，再执行对应方法
    """
    print(f'用户请求类型{type_id}收藏')
    if type_id == 1:
        add_result = add_article_to_knowledge(article_data=data_dict, label_id=label_id, user_id=user_id)
    elif type_id == 2:
        add_result = add_patent_to_knowledge(patent_data=data_dict, label_id=label_id, user_id=user_id)
    elif type_id == 3:
        add_result = add_online_infomation_to_knowledge(online_infomation=data_dict, label_id=label_id, user_id=user_id)
    elif type_id == 4:
        add_result = add_mycontent_to_knowledge(content=data_dict['content_string'], title=data_dict['title_string'], label_id=label_id, user_id=user_id)
    elif type_id == 5:
        # 前端传入格式: data_dict = { "data": [ {file1}, {file2}, ... ] }
        from services.ragflow_service import (
            upload_to_ragflow_by_id,
            start_parsing_document_by_id,
            create_new_dataset,
        )

        file_list = data_dict.get('data', [])
        if not file_list:
            return {"code": 400, "msg": "未传入文件数据", "data": None}

        rag_dataset_rows = sqlite_execute(
            "SELECT ragflow_id FROM `个人知识库绑定` WHERE 用户id=?", (user_id,)
        )
        if not rag_dataset_rows:
            user_name = sqlite_execute("SELECT name FROM `user` WHERE id=?", (user_id,))
            rag_dataset_id = create_new_dataset(f"用户{user_name[0]['name']}的个人知识库")
            sqlite_execute(
                "INSERT INTO `个人知识库绑定` (用户id, ragflow_id) VALUES (?, ?)",
                (user_id, rag_dataset_id),
            )
            print(f"创建rag知识库成功，id为：{rag_dataset_id}")
        else:
            rag_dataset_id = rag_dataset_rows[0]['ragflow_id']
            print(f"rag知识库id为：{rag_dataset_id}")

        for idx, file_item in enumerate(file_list):
            print(f"正在添加第 {idx + 1}/{len(file_list)} 个文件: {file_item.get('title_string', '未知')}")
            add_result = add_mycontent_file_to_knowledge(
                file_base64_string=file_item['file_base64_string'],
                file_extension=file_item['file_extension'],
                title=file_item['title_string'],
                label_id=label_id,
                user_id=user_id
            )
            if add_result['code'] != 200:
                return add_result

            latest = sqlite_execute(
                "SELECT id, mark_info FROM `knowledgebase` WHERE user_id=? ORDER BY id DESC LIMIT 1",
                (user_id,),
            )
            latest_knowledge_id = latest[0]['id']
            mark_info = json.loads(latest[0]['mark_info'])
            file_path = f"file_data/{mark_info['filename']}"
            file_ext = str(file_item['file_extension']).replace(".", "")
            safe_title = re.sub(
                r'[<>:"/\\|?*\n\r\t]', '_', str(file_item['title_string']).strip()
            )[:200] or "untitled"
            upload_filename = f"{safe_title}.{file_ext}"

            try:
                rag_file_id = upload_to_ragflow_by_id(
                    file_path, rag_dataset_id, upload_filename=upload_filename
                )
                sqlite_execute(
                    "UPDATE `knowledgebase` SET rag_id=? WHERE id=?",
                    (rag_file_id, latest_knowledge_id),
                )
                start_parsing_document_by_id(rag_dataset_id, [rag_file_id])
                print(f"上传并解析第{idx + 1}个文件至rag知识库成功，id为：{rag_file_id}")
            except Exception as e:
                print(f"上传第{idx + 1}个文件至rag知识库失败: {e}")
                return {"code": 500, "msg": f"第{idx + 1}个文件上传失败: {e}", "data": None}

        return {"code": 200, "msg": "success", "data": None}
    else:
        return {"code": 500, "msg": "收藏类型错误"}

    #执行完收藏后，查询当前用户id下最新收藏的id和标题
    latest_row = sqlite_execute(
        "SELECT id, title FROM `knowledgebase` WHERE user_id=? ORDER BY id DESC LIMIT 1",
        (user_id,),
    )
    latest_knowledge_id = latest_row[0]['id']
    knowledge_title = str(latest_row[0]['title']).strip()

    if add_result['code'] == 200:
        from services.ragflow_service import upload_to_ragflow_by_id

        #先判断当前用户下是否存在rag知识库id，如果不存在，则创建一个
        rag_dataset_id = sqlite_execute("SELECT ragflow_id FROM `个人知识库绑定` WHERE 用户id=?", (user_id,))
        if not rag_dataset_id:
            #如果不存在，则以用户名字创建一个rag知识库
            user_name = sqlite_execute("SELECT name FROM `user` WHERE id=?", (user_id,))
            from services.ragflow_service import create_new_dataset
            rag_dataset_id = create_new_dataset(f"用户{user_name[0]['name']}的个人知识库")
            sqlite_execute("INSERT INTO `个人知识库绑定` (用户id, ragflow_id) VALUES (?, ?)", (user_id, rag_dataset_id))
            print(f"创建rag知识库成功，id为：{rag_dataset_id}")
        else:
            rag_dataset_id = rag_dataset_id[0]['ragflow_id']
            print(f"rag知识库id为：{rag_dataset_id}")
        #如果收藏内容类型是1-4文本，则临时变为txt文件，再上传至rag知识库
        if type_id in [1, 2, 3, 4]:
            safe_title = re.sub(r'[<>:"/\\|?*\n\r\t]', '_', knowledge_title)[:200] or "untitled"
            file_path = f"file_data/{safe_title}.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(str(data_dict))
            rag_file_id = upload_to_ragflow_by_id(file_path, rag_dataset_id)
            os.remove(file_path)
            print(f"上传至rag知识库成功，id为：{rag_file_id}")

            #将rag的文件id更新到知识库表
            sqlite_execute("UPDATE `knowledgebase` SET rag_id=? WHERE id=?", (rag_file_id, latest_knowledge_id))


            #触发rag知识库的指定文档解析
            from services.ragflow_service import start_parsing_document_by_id
            start_parsing_document_by_id(rag_dataset_id, [rag_file_id])
            return {"code": 200, "msg": "success", "data": None}
    



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
    res = await loop.run_in_executor(executor, aiping_ai_answer, full_prompt)

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
        
    # 4. 先插入公共知识库数据库表获取知识 ID
    _, ext = os.path.splitext(original_filename)
    file_type = ext.lstrip(".").lower()
    file_size = len(file_bytes)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    description = ""
    tags_json = json.dumps([], ensure_ascii=False)
    
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

    # 5. 写入公共服务磁盘对应文件专属目录 (以知识 id 命名)
    UPLOAD_ROOT = "./file_data/public_db"
    save_dir = os.path.join(UPLOAD_ROOT, str(new_id))
    os.makedirs(save_dir, exist_ok=True)
 
    abs_path = os.path.join(save_dir, original_filename)
    rel_path = f"public_db/{new_id}/{original_filename}"
 
    try:
        with open(abs_path, "wb") as f:
            f.write(file_bytes)
    except Exception as e:
        sqlite_execute("DELETE FROM publicDatabase_file WHERE id=?", (new_id,))
        raise HTTPException(status_code=500, detail=f"写入转移文件失败: {e}")
        
    # 6. 更新路径并调用 RagFlow
    sqlite_execute("UPDATE publicDatabase_file SET file_path=? WHERE id=?", (rel_path, new_id))
    
    try:
        from services.ragflow_service import upload_to_ragflow, start_parsing_document
        ragflow_result = upload_to_ragflow(abs_path)
        
        document_id = None
        if ragflow_result and ragflow_result.get("code") == 0 and ragflow_result.get("data"):
            document_id = ragflow_result["data"][0]["id"]
            start_parsing_document([document_id])
            sqlite_execute("UPDATE publicDatabase_file SET ragflow_id=? WHERE id=?", (document_id, new_id))
            
    except Exception as e:
        if os.path.exists(abs_path):
            os.remove(abs_path)
        raise HTTPException(status_code=500, detail=f"RAGFlow 解析失败: {e}")
        
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


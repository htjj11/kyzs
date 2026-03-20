'''
从数据库获取知识接口
'''
import asyncio
from concurrent.futures import ThreadPoolExecutor

from services.chat_service import delete_anything_knowledge_by_knowledgeId_api

from fastapi import APIRouter, Request, Body
from services.literature_service import siliconflow_deepseek_answer
from core.utils import extract_json
from core.sqlLiteExec import sqlite_execute
import base64
import os
executor = ThreadPoolExecutor()

router = APIRouter(
    prefix="/get_knowledge",
    tags=["与知识库相关的操作接口"],
)



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

        anything_result = sqlite_execute(
            "SELECT id FROM `anything_db` WHERE knowledge_id=?", (item['id'],)
        )
        item['in_anything'] = 1 if anything_result else 0

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
    try:
        delete_anything_knowledge_by_knowledgeId_api(knowledge_id)
    except Exception as e:
        print(f'删除anythingLLM知识库失败：{e}')
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
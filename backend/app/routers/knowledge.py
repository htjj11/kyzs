'''
从数据库获取知识接口
'''
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.services.chat_service import delete_anything_knowledge_by_knowledgeId_api
from app.core.database import db as kyzs_sql
from fastapi import APIRouter, Request, Body
from app.services.literature_service import siliconflow_deepseek_answer
from app.core.utils import extract_json

executor = ThreadPoolExecutor()

router = APIRouter(
    prefix="/get_knowledge",
    tags=["与知识库相关的操作接口"],
)


@router.post("/get_all_knowledge")
async def get_all_label(
    request: Request,
    user_id: int = Body(..., embed=True, description="用户id")
):
    res = kyzs_sql.mysql_exec("SELECT * FROM `knowledgebase` WHERE user_id=%s", (user_id,))

    for item in res:
        label_result = kyzs_sql.mysql_exec(
            "SELECT label_name FROM `label` WHERE id=%s", (item['label_id'],)
        )
        item['label_name'] = label_result[0]['label_name'] if label_result else '未定义'

        anything_result = kyzs_sql.mysql_exec(
            "SELECT id FROM `anything_db` WHERE knowledge_id=%s", (item['id'],)
        )
        item['in_anything'] = 1 if anything_result else 0

    return {"code": 200, "msg": 'success', "data": res}


@router.post("/delete_knoledge_by_id")
async def delete_knoledge_by_id(
    request: Request,
    knowledge_id: int = Body(..., embed=True, description="知识id")
):
    res = kyzs_sql.mysql_exec("DELETE FROM `knowledgebase` WHERE id=%s", (knowledge_id,))
    delete_anything_knowledge_by_knowledgeId_api(knowledge_id)
    return {"code": 200, "msg": 'success', "data": res}


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
    res = kyzs_sql.mysql_exec(
        """UPDATE `knowledgebase`
           SET title=%s, content=%s, label_id=%s, type_id=%s, mark_info=%s
           WHERE id=%s""",
        (knowledge_title, knowledge_content, knowledge_label, knowledge_type, knowledge_mark_info, knowledge_id)
    )
    return {"code": 200, "msg": 'success', "data": res}


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

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
import re

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
    """
    获取当前用户id下的所有知识
    """
    sql_sentence = f"""
    SELECT * FROM `knowledgebase` where user_id={user_id}
    """
    res = kyzs_sql.mysql_exec(sql_sentence)

    for item in res:
        label_id = item['label_id']
        sql_sentence = f"""
        SELECT label_name FROM `label` WHERE id={label_id}
        """
        result = kyzs_sql.mysql_exec(sql_sentence)
        label_name = result[0]['label_name'] if result and 'label_name' in result[0] else '未定义'
        item['label_name'] = label_name

        knowledge_id = item['id']
        sql_sentence = f"""
        SELECT id FROM `anything_db` WHERE knowledge_id={knowledge_id}
        """
        result = kyzs_sql.mysql_exec(sql_sentence)
        item['in_anything'] = 1 if result and 'id' in result[0] else 0

    return {"code": 200, "msg": 'success', "data": res}


@router.post("/delete_knoledge_by_id")
async def delete_knoledge_by_id(
    request: Request,
    knowledge_id: int = Body(..., embed=True, description="知识id")
):
    """
    根据知识id删除知识
    """
    sql_sentence = f"""
    DELETE FROM `knowledgebase` where id={knowledge_id}
    """
    res = kyzs_sql.mysql_exec(sql_sentence)

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
    """
    根据知识id更新知识
    """
    sql_sentence = f"""
    UPDATE `knowledgebase` SET 
    title='{knowledge_title}',
    content='{knowledge_content}',
    label_id={knowledge_label},
    type_id={knowledge_type},
    mark_info='{knowledge_mark_info}'
    WHERE id={knowledge_id}
    """
    res = kyzs_sql.mysql_exec(sql_sentence)
    return {"code": 200, "msg": 'success', "data": res}


@router.post("/generate_content_by_ai")
async def generate_content_by_ai(
    request: Request,
    knowledge_content: str = Body(..., embed=True, description="知识内容"),
    prompt: str = Body(..., embed=True, description="提示词")
):
    """
    根据知识内容和提示词生成内容
    """
    prompt = '''
    请根据以下内容，生成符合提示词要求的内容：
    原始内容：{}
    用户需求提示词：{}

    '''.format(knowledge_content, prompt) + r"返回的生成内容请以json格式返回，格式为{content:'生成的内容'}"
    print('用户请求生成AI回复:', prompt)

    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(executor, siliconflow_deepseek_answer, prompt)

    data = extract_json(res)
    return {"code": 200, "msg": 'success', "data": data}

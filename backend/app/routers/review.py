'''
报告接口
'''
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core.database import db as kyzs_sql
from fastapi import APIRouter, Request, Body
from app.services.literature_service import (
    siliconflow_deepseek_answer,
    modify_summary_api,
    modify_review_new_api,
    generate_word_api,
    generate_fuwenben_word_api,
)

executor = ThreadPoolExecutor()

router = APIRouter(
    prefix="/get_review",
    tags=["获取所有综述相关设置"],
)


@router.post("/create_review")
async def create_review(
    request: Request,
    user_id: int = Body(..., embed=True, description="用户id"),
    title: str = Body(..., embed=True, description="报告的主题"),
):
    res = kyzs_sql.mysql_exec(
        "INSERT INTO `review_records` (title, completion_status, review_body, user_id) VALUES (%s, 0, '请从此处开始编辑', %s)",
        (title, user_id)
    )
    return {"code": 200, "msg": 'success', "data": res}


@router.post("/create_review_by_template")
async def create_review_by_template(
    request: Request,
    user_id: int = Body(..., embed=True, description="用户id"),
    title: str = Body(..., embed=True, description="报告的主题"),
    template_id: int = Body(..., embed=True, description="绑定的模板id")
):
    template = kyzs_sql.mysql_exec(
        "SELECT * FROM `review_template` WHERE id=%s", (template_id,)
    )
    template_content = template[0]['content']
    res = kyzs_sql.mysql_exec(
        "INSERT INTO `review_records` (title, completion_status, review_body, user_id, label_id) VALUES (%s, 0, %s, %s, %s)",
        (title, template_content, user_id, template_id)
    )
    return {"code": 200, "msg": 'success', "data": res}


@router.post("/delete_review")
async def delete_review(
    request: Request,
    review_id: int = Body(..., embed=True, description="报告id")
):
    res = kyzs_sql.mysql_exec("DELETE FROM `review_records` WHERE id=%s", (review_id,))
    return {"code": 200, "msg": 'success', "data": res}


@router.post("/get_all_review")
async def get_all_review(
    request: Request,
    user_id: int = Body(..., embed=True, description="用户id")
):
    res = kyzs_sql.mysql_exec("SELECT * FROM `review_records` WHERE user_id=%s", (user_id,))
    return {"code": 200, "msg": 'success', "data": res}


@router.post("/get_review_base64")
async def get_review_detail(
    request: Request,
    review_id: int = Body(..., embed=True, description="报告id")
):
    result = generate_word_api(review_id)
    return {"code": 200, "msg": 'success', "data": result}


@router.post("/get_review_fuwenben_base64")
async def get_review_fuwenben_base64(
    request: Request,
    review_id: int = Body(..., embed=True, description="报告id")
):
    result = generate_fuwenben_word_api(review_id)
    return {"code": 200, "msg": 'success', "data": result}


@router.post('/modify_review')
async def modify_review(
    request: Request,
    review_id: int = Body(..., embed=True, description="记录id"),
    start_position: int = Body(..., embed=True, description="目标文本起始位置"),
    end_position: int = Body(..., embed=True, description="目标文本结束位置"),
    replaced_text: str = Body(..., embed=True, description="替换文本"),
):
    print(f"用户请求 IP: {request.client.host}，记录id：{review_id}，目标文本起始位置：{start_position}，目标文本结束位置：{end_position}，替换文本：{replaced_text}")
    response = modify_summary_api(review_id, start_position, end_position, replaced_text)
    if response:
        return {"code": 200, "msg": "success", "data": None}
    return 0


@router.post("/modify_review_new")
async def modify_review_new(
    request: Request,
    review_id: int = Body(..., embed=True, description="记录id"),
    review_body: str = Body(..., embed=True, description="综述正文"),
):
    print(f"用户请求 IP: {request.client.host}，记录id：{review_id}，综述正文：{review_body}")
    response = modify_review_new_api(review_id, review_body)
    if response:
        return {"code": 200, "msg": "success", "data": None}
    return 0


@router.post('/get_summary_by_ai')
async def get_summary_by_ai(
    request: Request,
    knowledge_ids: list[int] = Body(..., embed=True, description="知识库id列表"),
    prompt_ids: list[int] = Body(..., embed=True, description="提示词id列表"),
    user_need: str = Body(..., embed=True, description="用户需求字符串"),
):
    if knowledge_ids:
        placeholders = ','.join(['%s'] * len(knowledge_ids))
        knowledge_rows = kyzs_sql.mysql_exec(
            f"SELECT content FROM knowledgebase WHERE id IN ({placeholders})",
            tuple(knowledge_ids)
        )
    else:
        knowledge_rows = []

    if prompt_ids:
        placeholders = ','.join(['%s'] * len(prompt_ids))
        prompt_rows = kyzs_sql.mysql_exec(
            f"SELECT text FROM prompt WHERE id IN ({placeholders})",
            tuple(prompt_ids)
        )
    else:
        prompt_rows = []

    knowledge_content = '\n'.join(r['content'] for r in knowledge_rows if r.get('content'))
    prompt_content = '\n'.join(r['text'] for r in prompt_rows if r.get('text'))

    prompt = f"""    
    知识库内容：
    {knowledge_content}
    格式\内容要求：
    {prompt_content}
    用户需求：
    {user_need}
    请你按照需求,直接回复用户,不需要多余的解释
    """
    print(prompt)
    summary = await asyncio.get_event_loop().run_in_executor(
        executor, siliconflow_deepseek_answer, prompt
    )
    return {"code": 200, "msg": "success", "data": summary}


@router.post("/get_all_template")
async def get_all_template(
    request: Request,
    user_id: int = Body(..., embed=True, description="用户id")
):
    res = kyzs_sql.mysql_exec("SELECT * FROM `review_template`")
    return {"code": 200, "msg": 'success', "data": res}

'''
报告接口
'''
import asyncio
from concurrent.futures import ThreadPoolExecutor

from core.sqlLiteExec import sqlite_execute
from fastapi import APIRouter, Request, Body
from services.third_party_source.aichat_api import (
    siliconflow_deepseek_answer
)
from services.report_service import (
    modify_review_new_api
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
    res = sqlite_execute(
        "INSERT INTO `review_records` (title, completion_status, review_body, user_id) VALUES (?, 0, '请从此处开始编辑', ?)",
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
    template = sqlite_execute(
        "SELECT * FROM `review_template` WHERE id=?", (template_id,)
    )
    template_content = template[0]['content']
    res = sqlite_execute(
        "INSERT INTO `review_records` (title, completion_status, review_body, user_id, label_id) VALUES (?, 0, ?, ?, ?)",
        (title, template_content, user_id, template_id)
    )
    return {"code": 200, "msg": 'success', "data": res}


@router.post("/delete_review")
async def delete_review(
    request: Request,
    review_id: int = Body(..., embed=True, description="报告id")
):
    res = sqlite_execute("DELETE FROM `review_records` WHERE id=?", (review_id,))
    return {"code": 200, "msg": 'success', "data": res}


@router.post("/get_all_review")
async def get_all_review(
    request: Request,
    user_id: int = Body(..., embed=True, description="用户id")
):
    res = sqlite_execute("SELECT * FROM `review_records` WHERE user_id=?", (user_id,))
    return {"code": 200, "msg": 'success', "data": res}

 
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

#基于互联网模型获取大模型回复
@router.post('/get_summary_by_ai')
async def get_summary_by_ai(
    request: Request,
    knowledge_ids: list[int] = Body(..., embed=True, description="知识库id列表"),
    prompt_ids: list[int] = Body(..., embed=True, description="提示词id列表"),
    user_need: str = Body(..., embed=True, description="用户需求字符串"),
):
    if knowledge_ids:
        placeholders = ','.join(['?'] * len(knowledge_ids))
        knowledge_rows = sqlite_execute(
            f"SELECT content FROM knowledgebase WHERE id IN ({placeholders})",
            tuple(knowledge_ids)
        )
    else:
        knowledge_rows = []

    if prompt_ids:
        placeholders = ','.join(['?'] * len(prompt_ids))
        prompt_rows = sqlite_execute(
            f"SELECT text FROM prompt WHERE id IN ({placeholders})",
            tuple(prompt_ids)
        )
    else:
        prompt_rows = []

    knowledge_content = '\n'.join(r['content'] for r in knowledge_rows if r.get('content'))
    prompt_content = '\n'.join(r['text'] for r in prompt_rows if r.get('text'))

    prompt = f"""你是一个专业的学术与文本分析助手。请严格基于以下提供的信息来响应最终的用户需求。

    ### 【知识库内容】
    {knowledge_content}

    ### 【格式与内容要求】
    {prompt_content}

    ### 【用户需求】
    {user_need}

    ### 【输出准则】
    1. 请严格围绕【用户需求】进行作答。
    2. 必须遵从【格式与内容要求】中的所有规范。
    3. 答案应尽量参考【知识库内容】所提供的事实。
    4. 请直接输出最终的回复内容，绝对不要包含任何多余的解释、开场白（如“好的”、“根据提供的内容”等）或过渡句。
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
    res = sqlite_execute("SELECT * FROM `review_template`")
    return {"code": 200, "msg": 'success', "data": res}

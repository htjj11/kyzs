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
    """
    创建一个报告
    """
    sql_sentence = f"""
    INSERT INTO `review_records` (title, completion_status, review_body, user_id)
    VALUES ('{title}', 0, '请从此处开始编辑', {user_id});
    """
    res = kyzs_sql.mysql_exec(sql_sentence)
    return {"code": 200, "msg": 'success', "data": res}


@router.post("/create_review_by_template")
async def create_review_by_template(
    request: Request,
    user_id: int = Body(..., embed=True, description="用户id"),
    title: str = Body(..., embed=True, description="报告的主题"),
    template_id: int = Body(..., embed=True, description="绑定的模板id")
):
    """
    根据模板创建报告
    """
    sql_sentence = f"""
    SELECT * FROM `review_template` WHERE id={template_id};
    """
    template_content = kyzs_sql.mysql_exec(sql_sentence)[0]['content']

    sql_sentence = f"""
    INSERT INTO `review_records` (title, completion_status, review_body, user_id,label_id)
    VALUES ('{title}', 0, '{template_content}', {user_id},{template_id});
    """
    res = kyzs_sql.mysql_exec(sql_sentence)
    return {"code": 200, "msg": 'success', "data": res}


@router.post("/delete_review")
async def delete_review(
    request: Request,
    review_id: int = Body(..., embed=True, description="报告id")
):
    """
    删除报告
    """
    sql_sentence = f"""
    DELETE FROM `review_records` WHERE id={review_id};  
    """
    res = kyzs_sql.mysql_exec(sql_sentence)
    return {"code": 200, "msg": 'success', "data": res}


@router.post("/get_all_review")
async def get_all_review(
    request: Request,
    user_id: int = Body(..., embed=True, description="用户id")
):
    """
    获取当前用户id下的报告
    """
    sql_sentence = f"""
    SELECT * FROM `review_records` where user_id={user_id}
    """
    res = kyzs_sql.mysql_exec(sql_sentence)
    return {"code": 200, "msg": 'success', "data": res}


@router.post("/get_review_base64")
async def get_review_detail(
    request: Request,
    review_id: int = Body(..., embed=True, description="报告id")
):
    """
    获取当前报告id下的base64编码
    """
    base64_string = generate_word_api(review_id)
    return {"code": 200, "msg": 'success', "data": base64_string}


@router.post("/get_review_fuwenben_base64")
async def get_review_fuwenben_base64(
    request: Request,
    review_id: int = Body(..., embed=True, description="报告id")
):
    """
    获取当前报告id下的base64编码（富文本）
    """
    base64_string = generate_fuwenben_word_api(review_id)
    return {"code": 200, "msg": 'success', "data": base64_string}


@router.post('/modify_review')
async def modify_review(
    request: Request,
    review_id: int = Body(..., embed=True, description="记录id"),
    start_position: int = Body(..., embed=True, description="目标文本起始位置"),
    end_position: int = Body(..., embed=True, description="目标文本结束位置"),
    replaced_text: str = Body(..., embed=True, description="替换文本"),
):
    """
    修改综述生成记录
    """
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
    """
    修改综述生成记录完成情况（全文替换）
    """
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
    """
    传入参考知识库id列表,提示词id列表,用户需求字符串，调用大模型生成综述
    """
    sql = f"""
        SELECT content FROM knowledgebase
        WHERE id IN ({','.join(map(str, knowledge_ids))})
    """
    knowledge_content = kyzs_sql.mysql_exec(sql)
    sql = f"""
        SELECT text FROM prompt
        WHERE id IN ({','.join(map(str, prompt_ids))})
    """
    prompt_content = kyzs_sql.mysql_exec(sql)
    knowledge_content = '\n'.join([item['content'] for item in knowledge_content if item.get('content')]) if knowledge_content else ''
    prompt_content = '\n'.join([item['text'] for item in prompt_content if item.get('text')]) if prompt_content else ''

    prompt = f'''    
    知识库内容：
    {knowledge_content}
    格式\内容要求：
    {prompt_content}
    用户需求：
    {user_need}
    请你按照需求,直接回复用户,不需要多余的解释
    '''
    print(prompt)

    summary = await asyncio.get_event_loop().run_in_executor(
        executor,
        siliconflow_deepseek_answer,
        prompt
    )

    return {"code": 200, "msg": "success", "data": summary}


@router.post("/get_all_template")
async def get_all_template(
    request: Request,
    user_id: int = Body(..., embed=True, description="用户id")
):
    """
    获取当前用户id下的报告模板
    """
    sql_sentence = f"""
    SELECT * FROM `review_template` 
    """
    res = kyzs_sql.mysql_exec(sql_sentence)
    return {"code": 200, "msg": 'success', "data": res}

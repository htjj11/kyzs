'''
报告接口
'''
from services.权限 import check_permission
import asyncio
from concurrent.futures import ThreadPoolExecutor

from core.sqlLiteExec import sqlite_execute
from fastapi import APIRouter, Request, Body
from fastapi.responses import JSONResponse
from services.第三方接口.大模型对话 import (
    aiping_ai_answer,
    changcheng_ai_answer
)
from services.report_service import (
    modify_review_new_api
)
executor = ThreadPoolExecutor()

router = APIRouter(
    prefix="/report",
    tags=["报告相关接口"],
)

#新建一个报告
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

#通过模板新建一个报告
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

#删除一个报告
@router.post("/delete_review")
async def delete_review(
    request: Request,
    review_id: int = Body(..., embed=True, description="报告id")
):
    res = sqlite_execute("DELETE FROM `review_records` WHERE id=?", (review_id,))
    return {"code": 200, "msg": 'success', "data": res}

#获取当前用户的所有报告
@router.post("/get_all_review")
async def get_all_review(
    request: Request,
    user_id: int = Body(..., embed=True, description="用户id")
):
    res = sqlite_execute("SELECT * FROM `review_records` WHERE user_id=?", (user_id,))
    return {"code": 200, "msg": 'success', "data": res}

#获取报告的word文档
@router.post("/get_report_fuwenben_base64")
async def get_report_fuwenben_base64(
    request: Request,
    review_id: int = Body(..., embed=True, description="报告id")
):
    from services.报告导出 import html_to_word_base64
    #从review表中获取report_content
    sql = "SELECT * FROM review_records WHERE id=?"
    data = sqlite_execute(sql, (review_id,))
    if not data:
        return {'code': 400, 'msg': '未找到该报告', 'data': None}
    report_content = data[0]['review_body']
    #将报告内容转换为word文档 
    result = html_to_word_base64(report_content)
    return {"code": 200, "msg": 'success', "data": result}


#修改报告内容（新版）
@router.post("/modify_review_new")
async def modify_review_new(
    request: Request,
    review_id: int = Body(..., embed=True, description="记录id"),
    review_body: str = Body(..., embed=True, description="综述正文"),
):
    print(f"用户请求修改综述 IP: {request.client.host}，记录id：{review_id}，")

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
    model_provider: str = Body(..., embed=True, description="模型提供者"),
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

    #判断模型提供商
    if model_provider == "siliconflow_deepseek":
        summary = await asyncio.get_event_loop().run_in_executor(
            executor, aiping_ai_answer, prompt
        )
    elif model_provider == "changcheng":
        summary = await asyncio.get_event_loop().run_in_executor(
            executor, changcheng_ai_answer, prompt
        )
        if isinstance(summary, str) and "失败" in summary:
            return JSONResponse(
                status_code=500,
                content={"code": 500, "msg": "error", "data": summary}
            )
    return {"code": 200, "msg": "success", "data": summary}

#获取所有模板（大家共用）
@router.post("/get_all_template")
async def get_all_template(
    request: Request,
    user_id: int = Body(..., embed=True, description="用户id")
):
    res = sqlite_execute("SELECT * FROM `review_template`")
    return {"code": 200, "msg": 'success', "data": res}


#编辑\增加模板
@router.post("/edit_template")
async def edit_template(
    request: Request,
    user_id: int = Body(..., embed=True, description="用户id"),
    template_id: int = Body(None, embed=True, description="模板id"),
    template_name: str = Body(..., embed=True, description="模板名称"),
    template_content: str = Body(..., embed=True, description="模板内容")
):
    #检查用户权限   
    if not check_permission(user_id, "report_template_edit:edit"):
        return {"code": 400, "msg": "无权限修改模板"}
        
    # 检查 template_id 是否存在于数据库中
    exists = False
    if template_id is not None:
        row = sqlite_execute("SELECT 1 FROM `review_template` WHERE id=?", (template_id,), fetch="one")
        if row:
            exists = True

    if exists:
        res = sqlite_execute("UPDATE `review_template` SET name=?, content=? WHERE id=?", (template_name, template_content, template_id))
    else:
        res = sqlite_execute("INSERT INTO `review_template` (name, content) VALUES (?, ?)", (template_name, template_content))
    return {"code": 200, "msg": 'success', "data": res}


#删除模板
@router.post("/delete_template")
async def delete_template(
    request: Request,
    user_id: int = Body(..., embed=True, description="用户id"),
    template_id: int = Body(..., embed=True, description="模板id")
):
    #检查用户权限
    if not check_permission(user_id, "report_template_edit:edit"):
        return {"code": 400, "msg": "无权限删除模板"}
        
    res = sqlite_execute("DELETE FROM `review_template` WHERE id=?", (template_id,))
    return {"code": 200, "msg": 'success', "data": res}
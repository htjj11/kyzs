'''
翻译相关接口
'''
import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Request, Body, BackgroundTasks
from app.services.translate_service import (
    translate_text_api,
    translate_text_list_api,
    create_new_translate_doc_mission,
    get_all_translate_doc_list_api,
    get_translate_doc_detail_api,
    del_translate_doc_api,
    get_translate_word_by_content_api,
    add_translate_word_api,
    update_translate_word_api,
    delete_translate_word_api,
)

executor = ThreadPoolExecutor()

router = APIRouter(
    prefix="/translate",
    tags=["翻译相关接口"],
)


@router.post('/translate_text')
async def translate_text(
    request: Request,
    text: str = Body(..., description="要翻译的文本"),
    translate_type: str = Body(..., description="翻译类型"),
    field_id: int = Body(..., description="领域id"),
):
    """
    翻译接口
    """
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(executor, translate_text_api, text, translate_type, field_id)
    if response:
        return response
    return 0


@router.post('/translate_text_list')
async def translate_text_list(
    request: Request,
    text_list: list = Body(..., description="要翻译的文本列表"),
    translate_type: str = Body(..., description="翻译类型"),
    field_id: int = Body(..., description="领域id"),
):
    response = translate_text_list_api(text_list, translate_type, field_id)
    if response:
        return response
    return 0


@router.post('/translate_doc')
async def translate_doc(
    request: Request,
    doc_base64: str = Body(..., description="要翻译的doc文件base64"),
    topic: str = Body(..., description="翻译主题"),
    user_id: int = Body(..., description="用户ID"),
    background_tasks: BackgroundTasks = None
):
    """
    翻译文档接口（后台任务异步执行）
    """
    response = background_tasks.add_task(create_new_translate_doc_mission, doc_base64, topic, user_id)
    print(f"用户{user_id}请求翻译文档")
    return {"code": 200, "msg": "success", "data": None}


@router.post('/get_all_translate_doc_list')
async def get_all_translate_doc_list(
    request: Request,
    user_id: int = Body(..., embed=True, description="用户ID"),
):
    """
    获取所有翻译文档列表（不包括文档base64）
    """
    response = get_all_translate_doc_list_api(user_id)
    if response:
        return response
    return 0


@router.post('/get_translate_doc_detail')
async def get_translate_doc_detail(
    request: Request,
    doc_id: int = Body(..., embed=True, description="文档ID"),
):
    """
    获取某个翻译文档详情（包括文档base64）
    """
    response = get_translate_doc_detail_api(doc_id)
    if response:
        return response
    return 0


@router.post('/delete_translate_doc')
async def delete_translate_doc(
    request: Request,
    doc_id: int = Body(..., embed=True, description="文档ID"),
):
    """
    删除某个翻译文档
    """
    response = del_translate_doc_api(doc_id)
    if response:
        return response
    return 0


@router.post('/get_translate_word_by_content')
async def get_translate_word_by_content(
    request: Request,
    content1: str = Body(..., embed=True, description="词汇内容"),
):
    """
    根据单词获取匹配的词汇
    """
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(executor, get_translate_word_by_content_api, content1)
    if response['code'] == 200:
        return response
    return {'code': 404, 'msg': '词汇不存在', 'data': None}


@router.post('/add_translate_word')
async def add_translate_word(
    request: Request,
    ts_type: str = Body(..., description="翻译类型（如：en,zh等）"),
    field_id: int = Body(..., description="领域ID"),
    content1: str = Body(..., description="单词语言1（通常为英文）"),
    content2: str = Body(..., description="单词释义2（通常为中文释义的简写）"),
    content3: str = Body(..., description="单词用法3（包括注释，以及什么情况下该用什么content2）"),
    from_source: str = Body(..., description="该条单词的来源（比如xxxx字典）"),
):
    """
    添加新的翻译词汇
    """
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(executor, add_translate_word_api,
                                          ts_type, field_id, content1, content2, content3, from_source)
    if response:
        return response
    return {'code': 500, 'msg': '添加失败', 'data': None}


@router.post('/update_translate_word')
async def update_translate_word(
    request: Request,
    word_id: int = Body(..., description="词汇ID"),
    ts_type: str = Body(None, description="翻译类型（如：en,zh等）"),
    field_id: int = Body(None, description="领域ID"),
    content1: str = Body(None, description="单词语言1（通常为英文）"),
    content2: str = Body(None, description="单词释义2（通常为中文释义的简写）"),
    content3: str = Body(None, description="单词用法3（包括注释，以及什么情况下该用什么content2）"),
    from_source: str = Body(None, description="该条单词的来源（比如xxxx字典）"),
):
    """
    更新翻译词汇
    """
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(executor, update_translate_word_api,
                                          word_id, ts_type, field_id, content1, content2, content3, from_source)
    if response:
        return response
    return {'code': 500, 'msg': '更新失败', 'data': None}


@router.post('/delete_translate_word')
async def delete_translate_word(
    request: Request,
    word_id: int = Body(..., embed=True, description="词汇ID"),
):
    """
    删除翻译词汇
    """
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(executor, delete_translate_word_api, word_id)
    if response:
        return response
    return {'code': 500, 'msg': '删除失败', 'data': None}

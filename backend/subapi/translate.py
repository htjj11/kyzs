'''
翻译相关接口

'''
import asyncio
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor()  # 全局线程池，避免重复创建

from api.sql_role import kyzs_sql
from fastapi import APIRouter, Request,Body,BackgroundTasks
from api.api_fy import *


router = APIRouter(
    prefix="/translate",        # 给该模块统一加前缀
    tags=["翻译相关接口"],       # 接口分组
)



##################翻译接口#######################
@router.post('/translate_text')
async def translate_text(
    request: Request,  # 添加 Request 对象以获取请求信息
    text: str = Body(..., description="要翻译的文本"),
    translate_type: str = Body(..., description="翻译类型"),#翻译类型
    field_id: int = Body(..., description="领域id"),#领域id
):
    """
    翻译接口
    :return:
    """
    loop = asyncio.get_running_loop()
    # response = await translate_text_api(text,translate_type,field_id)
    response = await loop.run_in_executor(executor, translate_text_api, text,translate_type,field_id)
    if response:
        return response
    return 0
@router.post('/translate_text_list')
async def translate_text_list(
    request: Request,  # 添加 Request 对象以获取请求信息
    text_list: list = Body(..., description="要翻译的文本列表"),
    translate_type: str = Body(..., description="翻译类型"),#翻译类型
    field_id: int = Body(..., description="领域id"),#领域id
):

    response = translate_text_list_api(text_list,translate_type,field_id)
    if response:
        return response
    return 0


@router.post('/translate_doc')
async def translate_doc(
    request: Request,  # 添加 Request 对象以获取请求信息
    doc_base64: str = Body(..., description="要翻译的doc文件base64"),
    topic: str = Body(..., description="翻译主题"),#翻译主题
    user_id: int = Body(..., description="用户ID"),#用户ID
    
    # 后台任务处理
    background_tasks: BackgroundTasks = None
):
    """
    翻译接口
    :return:
    """
    response = background_tasks.add_task(create_new_translate_doc_mission,doc_base64,topic,user_id)
    print(f"用户{user_id}请求翻译文档") 
    # response = create_new_translate_doc_mission(doc_base64,topic)
 
    return {"code": 200, "msg": "success", "data": None}

@router.post('/get_all_translate_doc_list')
async def get_all_translate_doc_list(
    request: Request,  # 添加 Request 对象以获取请求信息
    user_id: int = Body(...,embed=True, description="用户ID"),#用户ID
):
    """
    获取所有翻译文档列表(不包括文档base64因为比较大)
    :return:
    {
    "translate_doc_list": [
                {
                    "id": 19,
                    "name": "测试",
                    "status": 1
                },
                {
                    "id": 20,
                    "name": "测试",
                    "status": 0
                }
            ]
        }
    """
    response = get_all_translate_doc_list_api(user_id)
    if response:
        return response
    return 0

@router.post('/get_translate_doc_detail')
async def get_translate_doc_detail(
    request: Request,  # 添加 Request 对象以获取请求信息
    doc_id: int = Body(...,embed=True, description="文档ID"),
):
    """
    获取某个翻译文档详情(包括文档base64)
    :return:
    """
    response = get_translate_doc_detail_api(doc_id)
    if response:
        return response
    return 0

@router.post('/delete_translate_doc')
async def delete_translate_doc(
    request: Request,  # 添加 Request 对象以获取请求信息
    doc_id: int = Body(...,embed=True, description="文档ID"),
):
    """
    删除某个翻译文档
    :return:
    """
    response = del_translate_doc_api(doc_id)
    if response:
        return response
    return 0



##################翻译词汇表接口#######################


@router.post('/get_translate_word_by_content')
async def get_translate_word_by_content(
    request: Request,  # 添加 Request 对象以获取请求信息
    content1: str = Body(...,embed=True, description="词汇内容"),
):
    """
    根据单词获取匹配的词汇
    :param content1: 词汇内容
    :return: 翻译词汇详情
    """
    loop = asyncio.get_running_loop()   
    response = await loop.run_in_executor(executor, get_translate_word_by_content_api, content1)
    if response['code'] == 200:
        return response
    return {'code': 404, 'msg': '词汇不存在', 'data': None}

@router.post('/add_translate_word')
async def add_translate_word(
    request: Request,  # 添加 Request 对象以获取请求信息
    ts_type: str = Body(..., description="翻译类型（如：en,zh等）"),
    field_id: int = Body(..., description="领域ID"),
    content1: str = Body(..., description="单词语言1（通常为英文）"),
    content2: str = Body(..., description="单词释义2（通常为中文释义的简写）"),
    content3: str = Body(..., description="单词用法3（包括注释，以及什么情况下该用什么content2）"),
    from_source: str = Body(..., description="该条单词的来源（比如xxxx字典）"),
):
    """
    添加新的翻译词汇
    :return: 操作结果
    """
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(executor, add_translate_word_api, 
                                        ts_type, field_id, content1, content2, content3, from_source)
    if response:
        return response
    return {'code': 500, 'msg': '添加失败', 'data': None}

@router.post('/update_translate_word')
async def update_translate_word(
    request: Request,  # 添加 Request 对象以获取请求信息
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
    :return: 操作结果
    """
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(executor, update_translate_word_api, 
                                        word_id, ts_type, field_id, content1, content2, content3, from_source)
    if response:
        return response
    return {'code': 500, 'msg': '更新失败', 'data': None}

@router.post('/delete_translate_word')
async def delete_translate_word(
    request: Request,  # 添加 Request 对象以获取请求信息
    word_id: int = Body(...,embed=True, description="词汇ID"),
):
    """
    删除翻译词汇
    :param word_id: 词汇ID
    :return: 操作结果
    """
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(executor, delete_translate_word_api, word_id)
    if response:
        return response
    return {'code': 500, 'msg': '删除失败', 'data': None}


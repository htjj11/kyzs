'''
四种信息检索接口
'''
import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Request, Body
from app.services.literature_service import (
    get_articles_from_oillink,
    get_patents_from_oillink,
    get_online_infomation_api,
    get_article_from_juhe_api,
    get_article_from_wanfang_api,
    wangfang_patent,
)
from app.services.translate_service import translate_text_api
from app.core.database import db as kyzs_sql

executor = ThreadPoolExecutor()

router = APIRouter(
    prefix="/get_from_oilink",
    tags=["报告接口"],
)


@router.post("/get_articles")
async def get_articles(
    request: Request,
    keywords_list: list = Body(..., embed=True, description="关键词列表"),
    page: int = Body(1, embed=True, description="页码", ge=0),
    size: int = Body(10, embed=True, description="每页数量", ge=0),
    user_id: int = Body(1, embed=True, description="用户id")
):
    """
    文献检索接口
    """
    print(f"\033[32m用户请求 IP: {request.client.host}，关键词列表：{keywords_list}，页码：{page}，每页数量：{size}\033[0m")
    response = get_articles_from_oillink(keywords_list, page, size, user_id)
    if response:
        print(f'olilink检索内容{len(response)}')
        return {"code": 200, "msg": "success", "data": response}
    return {"code": 200, "data": []}


@router.post('/get_patent')
async def get_patent(
    request: Request,
    query: str = Body(..., embed=True, description="查询关键词"),
    page: int = Body(1, embed=True, description="页码", ge=0),
    size: int = Body(10, embed=True, description="每页数量", ge=0)
):
    """
    获取关键词搜索专利
    """
    response = get_patents_from_oillink(query, page, size)
    if response:
        print(f'用户收藏专利')
        return {"code": 200, "msg": "success", "data": response}
    return 0


@router.post('/get_online_infomation')
async def get_online_infomation(
    request: Request,
    keyword: str = Body(..., embed=True, description="关键词"),
):
    """
    获取互联网信息接口
    """
    print(f"\033[32m用户请求 IP: {request.client.host}，联网搜索关键词：{keyword}\033[0m")
    loop = asyncio.get_running_loop()
    try:
        response = await loop.run_in_executor(executor, get_online_infomation_api, keyword)
        return {"code": 200, "msg": "success", "data": response}
    except Exception as e:
        return {"code": 500, "msg": f"互联网信息查询出错: {str(e)}"}


@router.post('/get_online_infomation_summary')
async def get_online_infomation_summary(
    request: Request,
    online_infomation: str = Body(..., embed=True, description="想要检索的关键词"),
):
    """
    获取互联网信息一篇摘要
    """
    print(f"\033[32m用户请求 IP: {request.client.host}，联网搜索关键词：{online_infomation}\033[0m")
    try:
        response = get_online_infomation_api(online_infomation)
        print(f'讯飞接口返回内容{response}')
        return {"code": 200, "msg": "success", "data": response}
    except Exception as e:
        return {"code": 500, "msg": f"互联网信息摘要出错: {str(e)}"}


@router.post('/get_article_from_juhe')
async def get_article_from_juhe(
    request: Request,
    exp: list = Body(..., embed=True, description="查询表达式"),
    date: str = Body(None, embed=True, description="年份"),
    page: int = Body(1, embed=True, description="页码", ge=0),
    size: int = Body(10, embed=True, description="每页数量", ge=0)
):
    """
    获取重庆聚合文章接口
    """
    print(f"\033[32m用户请求 IP: {request.client.host}，查询表达式：{exp}，年份：{date}，页码：{page}，每页数量：{size}\033[0m")
    response = get_article_from_juhe_api(exp, date, page, size)
    if response:
        return {"code": 200, "msg": "success", "data": response}
    return {"code": 200, "data": []}


@router.post('/get_article_from_wanfang')
async def get_article_from_wanfang(
    request: Request,
    exp: list = Body(..., embed=True, description="查询表达式"),
    date: int = Body(None, embed=True, description="年份"),
    page: int = Body(1, embed=True, description="页码", ge=0),
    user_id: int = Body(None, embed=True, description="用户id")
):
    """
    获取万芳文章接口
    """
    print(f"\033[32m用户请求 IP: {request.client.host}，查询表达式：{exp}，年份：{date}，页码：{page}\033[0m")
    try:
        response, total_count = get_article_from_wanfang_api(Datewithin=date, Keywords=exp, StartRecord=1+(page-1)*10, MaximumRecords=10)
        print(f'万方检索内容:{response}')
    except Exception as e:
        print(f'万方检索出错{str(e)}')
        return {"code": 500, "msg": f"万芳文章查询出错: {str(e)}"}
    if response:
        for paper_info in response:
            DOI = paper_info['DOI']
            sql_sentence = f"""
            SELECT * FROM `knowledgebase` WHERE user_id={user_id} AND mark_info='{DOI}';
            """
            mark_info = kyzs_sql.mysql_exec(sql_sentence)
            paper_info['is_collected'] = 1 if mark_info else 0

        return {"code": 200, "msg": "success", "data": response, "total_count": total_count}
    return {"code": 200, "data": []}


@router.post('/translate_keyword')
async def translate_keyword(
    request: Request,
    keyword: str = Body(..., embed=True, description="查询关键词"),
):
    """
    获取关键词翻译
    """
    print(f"\033[32m用户请求 IP: {request.client.host}，查询关键词：{keyword}\033[0m")
    response = translate_text_api(keyword, 'en2zh', 1)
    if response:
        return {"code": 200, "msg": "success", "data": response}
    return {"code": 200, "data": []}


@router.post('/get_patent_from_wanfang')
async def get_patent_from_wanfang(
    request: Request,
    exp: list = Body(..., embed=True, description="查询表达式"),
    date: int = Body(None, embed=True, description="年份"),
    page: int = Body(1, embed=True, description="页码", ge=0),
    user_id: int = Body(None, embed=True, description="用户id")
):
    """
    获取万芳专利接口
    """
    print(f"\033[32m用户请求 IP: {request.client.host}，查询表达式：{exp}，年份：{date}，页码：{page}\033[0m")
    try:
        response, total_count = wangfang_patent(Datewithin=date, patent_name=exp, StartRecord=1+(page-1)*10, MaximumRecords=10)
        print(f'万方检索内容:{response}')
        for paper_info in response:
            patent_id = paper_info['公开号']
            sql_sentence = f"""
            SELECT * FROM `knowledgebase` WHERE user_id={user_id} AND mark_info='{patent_id}';
            """
            mark_info = kyzs_sql.mysql_exec(sql_sentence)
            paper_info['is_collected'] = 1 if mark_info else 0

        return {"code": 200, "msg": "success", "data": response, "total_count": total_count}
    except Exception as e:
        print(f'万方检索出错{str(e)}')
        return {"code": 500, "msg": f"万芳专利查询出错: {str(e)}"}

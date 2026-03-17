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

import re

executor = ThreadPoolExecutor()


def _extract_year(value) -> int | None:
    """从各种日期格式中提取年份数字"""
    if value is None:
        return None
    s = str(value)
    m = re.search(r'\d{4}', s)
    return int(m.group()) if m else None


def _year_in_range(year, start_year, end_year) -> bool:
    """判断年份是否在范围内，year 可以是 int/str/None"""
    y = int(year) if year is not None else None
    if y is None:
        return True
    if start_year and y < start_year:
        return False
    if end_year and y > end_year:
        return False
    return True


def _strip_html(text):
    """去除 HTML 标签"""
    return re.sub(r'<[^>]+>', '', str(text)) if text else ''


# =================== 归一化：文献 ===================

def _normalize_oilink_article(item):
    kw = item.get('keywords_zh') or item.get('keywords') or []
    return {
        'title': _strip_html(item.get('title_zh') or item.get('title') or ''),
        'keywords': ', '.join(kw) if isinstance(kw, list) else str(kw),
        'year': str(item.get('year', '')),
        'abstract': item.get('abstract_zh') or item.get('abstract') or '',
        'doi': item.get('doi', ''),
        'source': 'OilLink',
        'is_collected': item.get('is_collected', 0),
        'download_url': None,
        '_raw': item,
    }


def _normalize_juhe_article(item):
    return {
        'title': item.get('标题', ''),
        'keywords': item.get('关键词', ''),
        'year': str(item.get('年份', '')),
        'abstract': item.get('摘要', ''),
        'doi': item.get('DOI', ''),
        'source': '聚合',
        'is_collected': 0,
        'download_url': item.get('下载链接'),
        '_raw': item,
    }


def _normalize_wanfang_article(item):
    return {
        'title': item.get('标题', ''),
        'keywords': item.get('关键词', ''),
        'year': str(item.get('发表时间', '')),
        'abstract': item.get('摘要', ''),
        'doi': item.get('DOI', ''),
        'source': '万方',
        'is_collected': item.get('is_collected', 0),
        'download_url': None,
        '_raw': item,
    }


# =================== 归一化：专利 ===================

def _extract_multilang_text(obj, prefer='zh'):
    """从 OilLink 多语言对象 {"en": ["text"], "zh": ["文本"]} 中提取文本"""
    if not isinstance(obj, dict):
        return _strip_html(str(obj)) if obj else ''
    if prefer in obj and obj[prefer]:
        return obj[prefer][0] if isinstance(obj[prefer], list) else str(obj[prefer])
    first = next(iter(obj.values()), None)
    if isinstance(first, list) and first:
        return first[0]
    return str(first) if first else ''


def _extract_name_list(obj):
    """从 OilLink 人员数组 [{"name":"xxx","sequence":0},...] 中提取姓名"""
    if isinstance(obj, list):
        names = [
            a.get('name', '') for a in sorted(obj, key=lambda x: x.get('sequence', 0))
            if isinstance(a, dict) and a.get('name')
        ]
        return ', '.join(names)
    return str(obj) if obj else ''


def _date_to_str(val):
    """将 datetime 或字符串转为 YYYY-MM-DD 格式"""
    if val is None or val == '':
        return ''
    s = str(val)
    return s.split('T')[0].split(' ')[0] if ('T' in s or ' ' in s) else s


_COUNTRY_MAP = {
    'us': '美国', 'cn': '中国', 'jp': '日本', 'de': '德国',
    'fr': '法国', 'uk': '英国', 'kr': '韩国', 'ru': '俄罗斯',
    'ca': '加拿大', 'au': '澳大利亚', 'es': '西班牙',
}


def _normalize_oilink_patent(item):
    raw_country = str(item.get('country', '')).lower()
    return {
        'title': _extract_multilang_text(item.get('title')),
        'applicant': _extract_name_list(item.get('applicant')),
        'inventor': _extract_name_list(item.get('inventor')),
        'app_date': _date_to_str(item.get('app_date')),
        'pub_date': _date_to_str(item.get('pub_date')),
        'app_num': item.get('app_num', ''),
        'pub_num': item.get('pub_num', ''),
        'abstract': _extract_multilang_text(item.get('abstract')),
        'country': _COUNTRY_MAP.get(raw_country, raw_country),
        'source': 'OilLink',
        'is_collected': item.get('is_collected', 0),
        '_raw': item,
    }


def _normalize_wanfang_patent(item):
    return {
        'title': item.get('专利名称', ''),
        'applicant': item.get('申请人', ''),
        'inventor': item.get('发明人', ''),
        'app_date': item.get('申请日', ''),
        'pub_date': item.get('公开日', ''),
        'app_num': item.get('申请号', ''),
        'pub_num': item.get('公开号', ''),
        'abstract': item.get('摘要', ''),
        'country': 'CN',
        'source': '万方',
        'is_collected': item.get('is_collected', 0),
        '_raw': item,
    }


router = APIRouter(
    prefix="/get_from_oilink",
    tags=["报告接口"],
)


@router.post("/get_articles")
async def get_articles(
    request: Request,
    keywords_list: list = Body(..., embed=True, description="关键词列表"),
    start_year: int = Body(None, embed=True, description="起始年份"),
    end_year: int = Body(None, embed=True, description="结束年份"),
    page: int = Body(1, embed=True, description="页码", ge=0),
    size: int = Body(10, embed=True, description="每页数量", ge=0),
    user_id: int = Body(1, embed=True, description="用户id")
):
    """
    OilLink文献检索接口，API不支持日期参数，后端拿到结果后按年份范围过滤
    """
    print(f"\033[32m用户请求 IP: {request.client.host}，关键词列表：{keywords_list}，年份范围：{start_year}-{end_year}，页码：{page}，每页数量：{size}\033[0m")
    response = get_articles_from_oillink(keywords_list, page, size, user_id)
    if response:
        if start_year or end_year:
            response = [
                item for item in response
                if _year_in_range(item.get('year'), start_year, end_year)
            ]
        print(f'olilink检索内容{len(response)}')
        return {"code": 200, "msg": "success", "data": response}
    return {"code": 200, "data": []}


@router.post('/get_patent')
async def get_patent(
    request: Request,
    query: str = Body(..., embed=True, description="查询关键词"),
    start_year: int = Body(None, embed=True, description="起始年份"),
    end_year: int = Body(None, embed=True, description="结束年份"),
    page: int = Body(1, embed=True, description="页码", ge=0),
    size: int = Body(10, embed=True, description="每页数量", ge=0)
):
    """
    OilLink专利检索，API不支持日期参数，后端拿到结果后按年份范围过滤
    """
    response = get_patents_from_oillink(query, page, size)
    if response:
        if start_year or end_year:
            response = [
                item for item in response
                if _year_in_range(_extract_year(item.get('app_date')), start_year, end_year)
            ]
        print(f'oilink专利检索内容{len(response)}')
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
    date: str = Body(None, embed=True, description="年份（兼容旧接口）"),
    start_year: int = Body(None, embed=True, description="起始年份"),
    end_year: int = Body(None, embed=True, description="结束年份"),
    page: int = Body(1, embed=True, description="页码", ge=0),
    size: int = Body(10, embed=True, description="每页数量", ge=0)
):
    """
    重庆聚合文章接口，聚合API仅支持精确单年不支持范围，后端拿到结果后按年份范围过滤
    """
    print(f"\033[32m用户请求 IP: {request.client.host}，查询表达式：{exp}，年份范围：{start_year}-{end_year}，页码：{page}，每页数量：{size}\033[0m")
    response = get_article_from_juhe_api(exp, None, page, size)
    if response:
        if start_year or end_year:
            response = [
                item for item in response
                if _year_in_range(item.get('年份'), start_year, end_year)
            ]
        return {"code": 200, "msg": "success", "data": response}
    return {"code": 200, "data": []}


@router.post('/get_article_from_wanfang')
async def get_article_from_wanfang(
    request: Request,
    exp: list = Body(..., embed=True, description="查询表达式"),
    date: int = Body(None, embed=True, description="年份（兼容旧接口）"),
    start_year: int = Body(None, embed=True, description="起始年份"),
    end_year: int = Body(None, embed=True, description="结束年份"),
    page: int = Body(1, embed=True, description="页码", ge=0),
    user_id: int = Body(None, embed=True, description="用户id")
):
    """
    获取万芳文章接口，支持年份范围筛选
    """
    sy = start_year or date
    ey = end_year or date
    print(f"\033[32m用户请求 IP: {request.client.host}，查询表达式：{exp}，年份范围：{sy}-{ey}，页码：{page}\033[0m")
    try:
        response, total_count = get_article_from_wanfang_api(start_year=sy, end_year=ey, Keywords=exp, StartRecord=1+(page-1)*10, MaximumRecords=10)
        print(f'万方检索内容:{response}')
    except Exception as e:
        print(f'万方检索出错{str(e)}')
        return {"code": 500, "msg": f"万芳文章查询出错: {str(e)}"}
    if response:
        for paper_info in response:
            DOI = paper_info['DOI']
            mark_info = kyzs_sql.mysql_exec(
                "SELECT id FROM `knowledgebase` WHERE user_id=%s AND mark_info=%s",
                (user_id, DOI)
            )
            paper_info['is_collected'] = 1 if mark_info else 0

        if sy or ey:
            response = [
                item for item in response
                if _year_in_range(item.get('发表时间'), sy, ey)
            ]
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
    date: int = Body(None, embed=True, description="年份（兼容旧接口）"),
    start_year: int = Body(None, embed=True, description="起始年份"),
    end_year: int = Body(None, embed=True, description="结束年份"),
    page: int = Body(1, embed=True, description="页码", ge=0),
    user_id: int = Body(None, embed=True, description="用户id")
):
    """
    获取万芳专利接口，支持年份范围筛选
    """
    sy = start_year or date
    ey = end_year or date
    print(f"\033[32m用户请求 IP: {request.client.host}，查询表达式：{exp}，年份范围：{sy}-{ey}，页码：{page}\033[0m")
    try:
        response, total_count = wangfang_patent(start_year=sy, end_year=ey, patent_name=exp, StartRecord=1+(page-1)*10, MaximumRecords=10)
        print(f'万方检索内容:{response}')
        for paper_info in response:
            patent_id = paper_info['公开号']
            mark_info = kyzs_sql.mysql_exec(
                "SELECT id FROM `knowledgebase` WHERE user_id=%s AND mark_info=%s",
                (user_id, patent_id)
            )
            paper_info['is_collected'] = 1 if mark_info else 0

        if sy or ey:
            response = [
                item for item in response
                if _year_in_range(_extract_year(item.get('申请日')), sy, ey)
            ]
        return {"code": 200, "msg": "success", "data": response, "total_count": total_count}
    except Exception as e:
        print(f'万方检索出错{str(e)}')
        return {"code": 500, "msg": f"万芳专利查询出错: {str(e)}"}


# =================== 聚合检索（一搜多源） ===================

@router.post('/search_all_articles')
async def search_all_articles(
    request: Request,
    keywords: str = Body(..., embed=True, description="关键词，逗号分隔"),
    start_year: int = Body(None, embed=True, description="起始年份"),
    end_year: int = Body(None, embed=True, description="结束年份"),
    page: int = Body(1, embed=True, description="页码（从1开始）"),
    size: int = Body(20, embed=True, description="每个数据源每页条数"),
    user_id: int = Body(1, embed=True, description="用户id"),
):
    """
    聚合文献检索：并发查询 OilLink / 聚合 / 万方，归一化后按年份降序合并返回。
    向每个源各请求 size 条，合并后按年份排序全部返回。
    """
    kw_list = [k.strip() for k in keywords.split(',') if k.strip()]
    print(f"\033[32m聚合文献检索: keywords={kw_list}, year={start_year}-{end_year}, page={page}\033[0m")
    loop = asyncio.get_running_loop()

    def _fetch_oilink():
        try:
            data = get_articles_from_oillink(kw_list, page - 1, size, user_id)
            if not data:
                return []
            items = [_normalize_oilink_article(i) for i in data]
            if start_year or end_year:
                items = [i for i in items if _year_in_range(i['year'], start_year, end_year)]
            return items
        except Exception as e:
            print(f"OilLink文献检索出错: {e}")
            return []

    def _fetch_juhe():
        try:
            data = get_article_from_juhe_api(kw_list, None, page, size)
            if not data:
                return []
            items = [_normalize_juhe_article(i) for i in data]
            if start_year or end_year:
                items = [i for i in items if _year_in_range(i['year'], start_year, end_year)]
            return items
        except Exception as e:
            print(f"聚合文献检索出错: {e}")
            return []

    def _fetch_wanfang():
        try:
            data, total = get_article_from_wanfang_api(
                start_year=start_year, end_year=end_year,
                Keywords=kw_list, StartRecord=1 + (page - 1) * size, MaximumRecords=size
            )
            if not data:
                return []
            for paper in data:
                doi = paper.get('DOI', '')
                mark = kyzs_sql.mysql_exec(
                    "SELECT id FROM `knowledgebase` WHERE user_id=%s AND mark_info=%s",
                    (user_id, doi)
                )
                paper['is_collected'] = 1 if mark else 0
            items = [_normalize_wanfang_article(i) for i in data]
            if start_year or end_year:
                items = [i for i in items if _year_in_range(i['year'], start_year, end_year)]
            return items
        except Exception as e:
            print(f"万方文献检索出错: {e}")
            return []

    oilink_res, juhe_res, wanfang_res = await asyncio.gather(
        loop.run_in_executor(executor, _fetch_oilink),
        loop.run_in_executor(executor, _fetch_juhe),
        loop.run_in_executor(executor, _fetch_wanfang),
    )

    merged = list(oilink_res) + list(juhe_res) + list(wanfang_res)
    merged.sort(key=lambda x: _extract_year(x.get('year')) or 0, reverse=True)

    print(f"聚合文献结果: OilLink={len(oilink_res)}, 聚合={len(juhe_res)}, 万方={len(wanfang_res)}, 返回={len(merged)}")
    return {"code": 200, "msg": "success", "data": merged}


@router.post('/search_all_patents')
async def search_all_patents(
    request: Request,
    keywords: str = Body(..., embed=True, description="关键词，逗号分隔"),
    start_year: int = Body(None, embed=True, description="起始年份"),
    end_year: int = Body(None, embed=True, description="结束年份"),
    page: int = Body(1, embed=True, description="页码（从1开始）"),
    size: int = Body(20, embed=True, description="每个数据源每页条数"),
    user_id: int = Body(1, embed=True, description="用户id"),
):
    """
    聚合专利检索：并发查询 OilLink + 万方，归一化后按申请日降序合并返回。
    向每个源各请求 size 条，合并后按年份排序全部返回。
    """
    kw_list = [k.strip() for k in keywords.split(',') if k.strip()]
    kw_str = ' '.join(kw_list)
    print(f"\033[32m聚合专利检索: keywords={kw_list}, year={start_year}-{end_year}, page={page}\033[0m")
    loop = asyncio.get_running_loop()

    def _fetch_oilink():
        try:
            data = get_patents_from_oillink(kw_str, page - 1, size)
            if not data:
                return []
            items = [_normalize_oilink_patent(i) for i in data]
            if start_year or end_year:
                items = [i for i in items if _year_in_range(_extract_year(i['app_date']), start_year, end_year)]
            return items
        except Exception as e:
            print(f"OilLink专利检索出错: {e}")
            return []

    def _fetch_wanfang():
        try:
            data, total = wangfang_patent(
                start_year=start_year, end_year=end_year,
                patent_name=kw_list, StartRecord=1 + (page - 1) * size, MaximumRecords=size
            )
            if not data:
                return []
            for p in data:
                pid = p.get('公开号', '')
                mark = kyzs_sql.mysql_exec(
                    "SELECT id FROM `knowledgebase` WHERE user_id=%s AND mark_info=%s",
                    (user_id, pid)
                )
                p['is_collected'] = 1 if mark else 0
            items = [_normalize_wanfang_patent(i) for i in data]
            if start_year or end_year:
                items = [i for i in items if _year_in_range(_extract_year(i['app_date']), start_year, end_year)]
            return items
        except Exception as e:
            print(f"万方专利检索出错: {e}")
            return []

    oilink_res, wanfang_res = await asyncio.gather(
        loop.run_in_executor(executor, _fetch_oilink),
        loop.run_in_executor(executor, _fetch_wanfang),
    )

    merged = list(oilink_res) + list(wanfang_res)
    merged.sort(key=lambda x: _extract_year(x.get('app_date')) or 0, reverse=True)

    print(f"聚合专利结果: OilLink={len(oilink_res)}, 万方={len(wanfang_res)}, 返回={len(merged)}")
    return {"code": 200, "msg": "success", "data": merged}

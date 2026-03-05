'''
四种信息检索接口

'''
import asyncio
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor()  # 全局线程池，避免重复创建


from fastapi import APIRouter, Request,Body
from api.api_bg import *
from api.api_fy import translate_text_api

router = APIRouter(
    prefix="/get_from_oilink",        # 给该模块统一加前缀
    tags=["报告接口"],       # 接口分组
)

#检索

@router.post("/get_articles")
async def get_articles(
    request: Request,  # 添加 Request 对象以获取请求信息
    keywords_list: list = Body(...,embed=True, description="关键词列表"),
    page: int = Body(1, embed=True, description="页码", ge=0),
    size: int = Body(10, embed=True, description="每页数量", ge=0),
    user_id: int = Body(1, embed=True, description="用户id")
):
    """
    文献检索接口
    :param request: Request 对象，包含请求信息
    :param keywords_list: 关键词列表
    :param page: 页码
    :param size: 每页数量
    :return: 文献检索结果，样例：{'code': 200, 'msg': 'success', 'data': [{'abstract_zh': '直线型振动筛和...', 'id': '6860e2f5163c01c850d9987f', 'keywords': None, 'keywords_zh': ['钻井液振动筛', '双振型', '离散单元法', 'EDEM', '筛分效率'], 'title_zh': '基于离散单元法的双振型下钻井液振动筛不 同颗粒筛分效率对比研究 后印本', 'year': 2025}, {'abstract': 'The primary ..', 'abstract_zh': '的目的...', 'doi': '10.3969/j.issn.1000-6532.2025.02.012', 'id': '68108681163c01c850d8d66d', 'keywords': ['Mining processing engineering', 'Flotation', 'Barite', 'Waste drilling fluid', 'Inhibitors', 'Collectors', 'Mechanism study'], 'keywords_zh': ['矿物加工工程', '浮选', '重晶石', '废弃钻井液', '抑制剂', '捕收剂', '机理研究'], 'title': 'Flotation Recovery of Barite in Waste Drilling Fluids Using Novel Inhibitors', 'title_zh': '新型抑制剂对废弃钻井液中重晶石的浮选回收', 'year': 2025}]}

    """
    print(f"\033[32m用户请求 IP: {request.client.host}，关键词列表：{keywords_list}，页码：{page}，每页数量：{size}\033[0m")
    response = get_articles_from_oillink(keywords_list, page, size,user_id)
    if response:
        print(f'olilink检索内容{len(response)}')
        return {"code": 200, "msg": "success", "data": response}
    return {"code": 200,  "data": []}


@router.post('/get_patent')
async def get_patent(
    request: Request,  # 添加 Request 对象以获取请求信息
    query: str = Body(..., embed=True, description="查询关键词"),
    page: int = Body(1, embed=True, description="页码", ge=0),
    size: int = Body(10, embed=True, description="每页数量", ge=0)
):
    """
    获取关键词搜索专利
    :return:
    """
    response = get_patents_from_oillink(query, page, size)
    if response:
        print(f'用户收藏专利')
        return {"code": 200, "msg": "success", "data": response}
    return 0


@router.post('/get_online_infomation')
async def get_online_infomation(    
    request: Request,  # 添加 Request 对象以获取请求信息
    keyword: str = Body(..., embed=True, description="关键词"),
):
    """
    获取互联网信息接口
    :return: 互联网信息查询结果
    """
    # 使用线程池异步执行耗时的网络信息查询任务，避免阻塞事件循环

    print(f"\033[32m用户请求 IP: {request.client.host}，联网搜索关键词：{keyword}\033[0m")
    loop = asyncio.get_running_loop()
    try:
        response = await loop.run_in_executor(executor, get_online_infomation_api, keyword)
        return {"code": 200, "msg": "success", "data": response}
    except Exception as e:
        return {"code": 500, "msg": f"互联网信息查询出错: {str(e)}"}


@router.post('/get_online_infomation_summary')
async def get_online_infomation_summary(
    request: Request,  # 添加 Request 对象以获取请求信息
    online_infomation: str = Body(..., embed=True, description="想要检索的关键词"),
):
    """
    获取互联网信息一篇摘要
    :param online_infomation: 互联网信息
    :return: 互联网信息摘要
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
    request: Request,  # 添加 Request 对象以获取请求信息
    exp: list = Body(..., embed=True, description="查询表达式"),
    date: str = Body(None, embed=True, description="年份"),
    page: int = Body(1, embed=True, description="页码", ge=0),
    size: int = Body(10, embed=True, description="每页数量", ge=0)
):
    """
    获取重庆聚合文章接口
    :param exp: 查询表达式列表
    :param date: 年份
    :param page: 页码
    :param size: 每页数量
    :return: 文章列表
    """
    print(f"\033[32m用户请求 IP: {request.client.host}，查询表达式：{exp}，年份：{date}，页码：{page}，每页数量：{size}\033[0m")
    response = get_article_from_juhe_api(exp, date, page, size)
    if response:
        return {"code": 200, "msg": "success", "data": response}
    return {"code": 200,  "data": []}

@router.post('/get_article_from_wanfang')
async def get_article_from_wanfang(
    request: Request,  # 添加 Request 对象以获取请求信息
    exp: list = Body(..., embed=True, description="查询表达式"),
    date: int = Body(None, embed=True, description="年份"),
    page: int = Body(1, embed=True, description="页码", ge=0),
    user_id: int = Body(None, embed=True, description="用户id")

):
    """
    获取万芳文章接口
    :param exp: 查询表达式列表 ["石油","钻井"]
    :param date: 年份 2018 格式，查询的是当年的
    :param page: 页码
    :return: 文章列表
    """
    print(f"\033[32m用户请求 IP: {request.client.host}，查询表达式：{exp}，年份：{date}，页码：{page}\033[0m")
    # 转换为字符串格式
    try:
        response,total_count = get_article_from_wanfang_api(Datewithin=date, Keywords=exp, StartRecord = 1+(page-1)*10, MaximumRecords = 10)
        print(f'万方检索内容:{response}')
    except Exception as e:
        print(f'万方检索出错{str(e)}')
        return {"code": 500, "msg": f"万芳文章查询出错: {str(e)}"}
    if response:
        #遍历当前用户收藏，是否存在mark_info与response的记录重复的
        for paper_info in response:
            DOI = paper_info['DOI'] 
            # 检查是否存在mark_info与response的记录重复的
            sql_sentence = f"""
            SELECT * FROM `knowledgebase` WHERE user_id={user_id} AND mark_info='{DOI}';
            """
            mark_info = kyzs_sql.mysql_exec(sql_sentence)
            if mark_info:
                # 如果存在匹配记录，将paper_info['is_collected']设置为mark_info[0]['is_collected']
                paper_info['is_collected'] = 1
            else:
                paper_info['is_collected'] = 0


        return {"code": 200, "msg": "success", "data": response,"total_count":total_count}
    return {"code": 200,  "data": []}




@router.post('/translate_keyword')
async def translate_keyword(
    request: Request,  # 添加 Request 对象以获取请求信息
    keyword: str = Body(..., embed=True, description="查询关键词"),

):
    """
    获取关键词翻译
    :param keyword: 查询表达式列表
    :return: 结果
    """
    print(f"\033[32m用户请求 IP: {request.client.host}，查询关键词：{keyword}\033[0m")
    response = translate_text_api(keyword,'en2zh',1)
    if response:
        return {"code": 200, "msg": "success", "data": response}
    return {"code": 200,  "data": []}



@router.post('/get_patent_from_wanfang')
async def get_patent_from_wanfang(
    request: Request,  # 添加 Request 对象以获取请求信息
    exp: list = Body(..., embed=True, description="查询表达式"),
    date: int = Body(None, embed=True, description="年份"),
    page: int = Body(1, embed=True, description="页码", ge=0),
    user_id: int = Body(None, embed=True, description="用户id")
):
    """
    获取万芳专利接口
    :param exp: 查询表达式列表 ["石油","钻井"]
    :param date: 年份 2018 格式，查询的是当年的
    :param page: 页码
    :return: 文章列表
    """
    print(f"\033[32m用户请求 IP: {request.client.host}，查询表达式：{exp}，年份：{date}，页码：{page}\033[0m")
    # 转换为字符串格式
    try:
        # 样例：response = wangfang_patent(Datewithin="2018", patent_name=["石油", "钻井"], StartRecord = 1, MaximumRecords = 10)
        response,total_count = wangfang_patent(Datewithin=date, patent_name=exp , StartRecord = 1+(page-1)*10, MaximumRecords = 10)
        print(f'万方检索内容:{response}')
        #遍历当前用户收藏，是否存在mark_info与response的记录重复的
        for paper_info in response:
            patent_id = paper_info['公开号'] 
            # 检查是否存在mark_info与response的记录重复的
            sql_sentence = f"""
            SELECT * FROM `knowledgebase` WHERE user_id={user_id} AND mark_info='{patent_id}';
            """
            mark_info = kyzs_sql.mysql_exec(sql_sentence)
            if mark_info:
                # 如果存在匹配记录，将paper_info['is_collected']设置为mark_info[0]['is_collected']
                paper_info['is_collected'] = 1
            else:
                paper_info['is_collected'] = 0



        return {"code": 200, "msg": "success", "data": response,"total_count":total_count}
    except Exception as e:
        print(f'万方检索出错{str(e)}')
        return {"code": 500, "msg": f"万芳专利查询出错: {str(e)}"}
    


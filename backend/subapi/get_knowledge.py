'''
从数据库获取知识接口

'''
import asyncio
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor()  # 全局线程池，避免重复创建

from api.api_chat import delete_anything_knowledge_by_knowledgeId_api
from api.sql_role import kyzs_sql
from fastapi import APIRouter, Request,Body
from api.api_bg import *
from api.tools import extract_json
import re

router = APIRouter(
    prefix="/get_knowledge",        # 给该模块统一加前缀
    tags=["与知识库相关的操作接口"],       # 接口分组
)
@router.post("/get_all_knowledge")
async def get_all_label(
    request:Request,
    user_id:int = Body(...,embed=True,description="用户id")
):
    """
    获取当前用户id下的所有知识
    :return: 所有知识
    """
    sql_sentence = f"""
    SELECT * FROM `knowledgebase` where user_id={user_id}
    """
    res = kyzs_sql.mysql_exec(sql_sentence)

    #为每个知识增加一个字段，查询label_id绑定的标签名称
    for item in res:
        #为每个知识增加一个字段，查询label_id绑定的标签名称
        label_id = item['label_id']
        sql_sentence = f"""
        SELECT label_name FROM `label` WHERE id={label_id}
        """
        # 添加空值检查，防止查询结果为空时出错
        result = kyzs_sql.mysql_exec(sql_sentence)
        label_name = result[0]['label_name'] if result and 'label_name' in result[0] else '未定义'
        item['label_name'] = label_name

        #查询当前知识是否在anything知识库，如果存在则增加一个字段in_anything=1,否则为0
        knowledge_id = item['id']
        sql_sentence = f"""
        SELECT id FROM `anything_db` WHERE knowledge_id={knowledge_id}
        """
        # 添加空值检查，防止查询结果为空时出错
        result = kyzs_sql.mysql_exec(sql_sentence)
        item['in_anything'] = 1 if result and 'id' in result[0] else 0


    return {"code":200,"msg":'success',"data":res}

@router.post("/delete_knoledge_by_id")
async def delete_knoledge_by_id(
    request:Request,
    knowledge_id:int = Body(...,embed=True,description="知识id")
):
    """
    根据知识id删除知识
    :return: 删除结果
    """
    #先删除个人知识库的内容
    sql_sentence = f"""
    DELETE FROM `knowledgebase` where id={knowledge_id}
    """
    res = kyzs_sql.mysql_exec(sql_sentence)

    #通过api方式删除anything知识库的内容
    delete_anything_knowledge_by_knowledgeId_api(knowledge_id)
    return {"code":200,"msg":'success',"data":res}

@router.post("/update_knoledge_by_id")
async def update_knoledge_by_id(
    request:Request,
    knowledge_id:int = Body(...,embed=True,description="知识id"),
    knowledge_title:str = Body(...,embed=True,description="知识名称"),
    knowledge_content:str = Body(...,embed=True,description="知识内容"),
    knowledge_label:int = Body(...,embed=True,description="知识标签id"),
    knowledge_type:int = Body(...,embed=True,description="知识类型"),
    knowledge_mark_info:str = Body(...,embed=True,description="知识来源")
):
    """
    根据知识id更新知识
    :return: 更新结果
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
    return {"code":200,"msg":'success',"data":res}


@router.post("/generate_content_by_ai")
async def generate_content_by_ai(
    request:Request,
    knowledge_content:str = Body(...,embed=True,description="知识内容"),
    prompt:str = Body(...,embed=True,description="提示词")
):
    """
    根据知识内容和提示词生成内容
    :return: 生成内容
    """

    prompt = '''
    请根据以下内容，生成符合提示词要求的内容：
    原始内容：{}
    用户需求提示词：{}

    '''.format(knowledge_content,prompt)+r"返回的生成内容请以json格式返回，格式为{content:'生成的内容'}"
    print('用户请求生成AI回复:',prompt)
    
    # 使用线程池异步执行同步函数，避免阻塞事件循环
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(executor, siliconflow_deepseek_answer, prompt)

    # 3. 解析为 Python 字典
    data = extract_json(res)
    return {"code":200,"msg":'success',"data":data}

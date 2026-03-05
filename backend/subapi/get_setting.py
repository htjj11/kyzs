'''
设置接口

'''
import asyncio
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor()  # 全局线程池，避免重复创建

from api.sql_role import kyzs_sql
from fastapi import APIRouter, Request,Body
from api.api_bg import *

router = APIRouter(
    prefix="/get_setting",        # 给该模块统一加前缀
    tags=["获取所有与系统相关设置"],       # 接口分组
)
@router.post("/get_all_label")
async def get_all_label(
    request:Request,
    user_id:int = Body(...,embed=True,description="用户id")
):
    """
    获取当前用户id下的所有标签
    :return: 所有标签
    """
    sql_sentence = f"""
    SELECT * FROM `label` where user_id={user_id}
    """
    res = kyzs_sql.mysql_exec(sql_sentence)
    return {"code":200,"msg":'success',"data":res}

##############################################################################提示词操作
@router.post("/get_all_prompt")
async def get_all_prompt(
    request:Request,
    user_id:int = Body(...,embed=True,description="用户id")
):
    """
    获取当前用户id下的所有提示词
    :return: 所有提示词
    """
    #获取提示词
    sql_sentence = f"""
    SELECT * FROM `prompt` where user_id={user_id}  
    """
    prompt_result = kyzs_sql.mysql_exec(sql_sentence)
    return {"code":200,"msg":'success',"data":prompt_result}

@router.post("/add_prompt")
async def add_prompt(
    request:Request,
    user_id:int = Body(...,embed=True,description="用户id"),
    name:str = Body(...,embed=True,description="提示词名称"),
    text:str = Body(...,embed=True,description="提示词类型id"),
    type:int = Body(...,embed=True,description="提示词内容")

):
    """
    增加一个提示词
    :return: 增加结果
    """
    #获取提示词
    sql_sentence = f"""
    insert into `prompt` (user_id,name,text,type) values ({user_id},'{name}','{text}',{int(type)})
    """
    prompt_result = kyzs_sql.mysql_exec(sql_sentence)
    return {"code":200,"msg":'success',"data":prompt_result}

@router.post("/update_prompt")
async def update_prompt(
    request:Request,
    name:str = Body(...,embed=True,description="提示词名称"),
    text:str = Body(...,embed=True,description="提示词类型id"),
    type:int = Body(...,embed=True,description="提示词内容"),
    id:int = Body(...,embed=True,description="提示词id")
):
    """
    更新一个提示词
    :return: 更新结果
    """
    #获取提示词
    sql_sentence = f"""
    update `prompt` set name='{name}',text='{text}',type={int(type)} where id={id}
    """
    prompt_result = kyzs_sql.mysql_exec(sql_sentence)
    return {"code":200,"msg":'success',"data":prompt_result}

@router.post("/delete_prompt")
async def delete_prompt(
    request:Request,
    id:int = Body(...,embed=True,description="提示词id")
):
    """
    删除一个提示词
    :return: 删除结果
    """
    #获取提示词
    sql_sentence = f"""
    delete from `prompt` where id={id}
    """
    prompt_result = kyzs_sql.mysql_exec(sql_sentence)
    return {"code":200,"msg":'success',"data":prompt_result}



@router.post("/get_all_prompt_type")
async def get_all_prompt_type(
    request:Request,
    user_id:int = Body(...,embed=True,description="用户id")
):
    """
    获取当前用户id下的所有提示词类型
    :return: 所有提示词类型
    """
    #获取提示词类型
    sql_sentence = f"""
    SELECT * FROM `prompt_type` where user_id={user_id}
    """
    prompt_type_result = kyzs_sql.mysql_exec(sql_sentence)
    return {"code":200,"msg":'success',"data":prompt_type_result}


@router.post("/get_label")
async def get_label(
    request:Request,
    user_id:int = Body(...,embed=True,description="用户id"),
):
    """
    获取所有label  
    :return: 所有label
    """
    #获取提示词类型
    sql_sentence = f"""
    select * from `label` where user_id={user_id}
    """
    prompt_type_result = kyzs_sql.mysql_exec(sql_sentence)
    return {"code":200,"msg":'success',"data":prompt_type_result}






@router.post("/add_label")
async def add_label(
    request:Request,
    user_id:int = Body(...,embed=True,description="用户id"),
    label_name:str = Body(...,embed=True,description="标签名称"),
):
    """
    增加一个标签
    :return: 增加结果
    """
    #获取标签
    sql_sentence = f"""
    insert into `label` (user_id,label_name) values ({user_id},'{label_name}')
    """
    label_result = kyzs_sql.mysql_exec(sql_sentence)
    return {"code":200,"msg":'success',"data":label_result}


@router.post("/delete_label")
async def delete_label(
    request:Request,
    id:int = Body(...,embed=True,description="标签id")
):
    """
    删除一个标签
    :return: 删除结果
    """
    #获取标签
    sql_sentence = f"""
    delete from `label` where id={id}
    """
    label_result = kyzs_sql.mysql_exec(sql_sentence)
    return {"code":200,"msg":'success',"data":label_result}


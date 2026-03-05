'''
系统设置相关接口

'''
import asyncio
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor()  # 全局线程池，避免重复创建

from api.sql_role import kyzs_sql
from fastapi import APIRouter, Request,Body,BackgroundTasks
from api.api_fy import *


router = APIRouter(
    prefix="/system",        # 给该模块统一加前缀
    tags=["系统设置相关接口"],       # 接口分组
)

@router.post('/login')
async def login_api(
    request: Request,  # 添加 Request 对象以获取请求信息
    username: str = Body(..., embed=True, description="用户名"),
    password: str = Body(..., embed=True, description="密码"),
):
    """
    登录系统
    :return:
    """
    # 通过数据库查询是否存在用户名、密码相符的情况
    sql_sentence = f"""
    select id from `user` where name='{username}' and passwd='{password}'
    """
    user_result = kyzs_sql.mysql_exec(sql_sentence)
    #
    if user_result:
        return {"code":200,"msg":'success',"data":{"user_id":user_result[0]['id'],"user_name":username}}
    else:
        return {"code":400,"msg":'fail',"data":{"msg":"用户名或密码错误"}}
    return 0
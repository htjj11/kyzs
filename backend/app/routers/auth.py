'''
系统设置相关接口
'''
from app.core.database import db as kyzs_sql
from fastapi import APIRouter, Request, Body

router = APIRouter(
    prefix="/system",
    tags=["系统设置相关接口"],
)


@router.post('/login')
async def login_api(
    request: Request,
    username: str = Body(..., embed=True, description="用户名"),
    password: str = Body(..., embed=True, description="密码"),
):
    """
    登录系统
    """
    sql_sentence = f"""
    select id from `user` where name='{username}' and passwd='{password}'
    """
    user_result = kyzs_sql.mysql_exec(sql_sentence)
    if user_result:
        return {"code": 200, "msg": 'success', "data": {"user_id": user_result[0]['id'], "user_name": username}}
    else:
        return {"code": 400, "msg": 'fail', "data": {"msg": "用户名或密码错误"}}

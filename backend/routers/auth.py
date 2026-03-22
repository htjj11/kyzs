'''
系统认证相关接口
'''

from fastapi import APIRouter, Request, Body
from core.sqlLiteExec import sqlite_execute 
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
    user_result = sqlite_execute(
        "SELECT id FROM user WHERE name=? AND passwd=?",
        (username, password)
    )
    if user_result:
        return {"code": 200, "msg": 'success', "data": {"user_id": user_result[0]['id'], "user_name": username}}
    else:
        return {"code": 400, "msg": 'fail', "data": {"msg": "用户名或密码错误"}}
 
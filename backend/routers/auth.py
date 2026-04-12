'''
系统认证相关接口
'''

from fastapi import APIRouter, Request, Body
from core.sqlLiteExec import sqlite_execute 
router = APIRouter(
    prefix="/system",
    tags=["系统设置相关接口"],
)

#登录校验
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
        # 获取用户权限表
        sql = """
        SELECT permission
        FROM user_permissions
        WHERE user_id = ?
        """
        permission_result = sqlite_execute(sql, (user_result[0]['id'],))

        # 将 [{'permission': 'xxx'}, ...] 转换为 ['xxx', ...]
        permission_list = [item['permission'] for item in permission_result] if permission_result else []
        print("用户权限:", permission_list)
        return {"code": 200, "msg": 'success', "data": {"user_id": user_result[0]['id'], "user_name": username, "permission": permission_list}}

    else:
        return {"code": 400, "msg": 'fail', "data": {"msg": "用户名或密码错误"}}
 
#
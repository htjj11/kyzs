'''
用于校验用户权限

'''
from core.sqlLiteExec import sqlite_execute 

def check_permission(user_id: int, permission: str) -> bool:
    """
    校验用户权限
    """
    result = sqlite_execute(
        "SELECT * FROM user_permissions WHERE user_id=? AND permission=?",
        (user_id, permission)
    )
    return bool(result)
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

#获取全部个人知识库标签
@router.post("/get_all_label")
async def get_all_label(
        request: Request,
        user_id: int = Body(..., embed=True, description="用户id")
):
    res = sqlite_execute("SELECT * FROM `label` WHERE user_id=?", (user_id,))
    return {"code": 200, "msg": 'success', "data": res}

#获取全部个人提示词
@router.post("/get_all_prompt")
async def get_all_prompt(
        request: Request,
        user_id: int = Body(..., embed=True, description="用户id")
):
    result = sqlite_execute("SELECT * FROM `prompt` WHERE user_id=?", (user_id,))
    return {"code": 200, "msg": 'success', "data": result}


# 添加个人提示词
@router.post("/add_prompt")
async def add_prompt(
        request: Request,
        user_id: int = Body(..., embed=True, description="用户id"),
        name: str = Body(..., embed=True, description="提示词名称"),
        text: str = Body(..., embed=True, description="提示词类型id"),
        type: int = Body(..., embed=True, description="提示词内容")
):
    prompt_result = sqlite_execute(
        "INSERT INTO `prompt` (user_id, name, text, type) VALUES (?, ?, ?, ?)",
        (user_id, name, text, int(type))
    )
    print(prompt_result)
    return {"code": 200, "msg": 'success', "data": prompt_result}


# 修改个人提示词
@router.post("/update_prompt")
async def update_prompt(
        request: Request,
        name: str = Body(..., embed=True, description="提示词名称"),
        text: str = Body(..., embed=True, description="提示词类型id"),
        type: int = Body(..., embed=True, description="提示词内容"),
        id: int = Body(..., embed=True, description="提示词id")
):
    prompt_result = sqlite_execute(
        "UPDATE `prompt` SET name=?, text=?, type=? WHERE id=?",
        (name, text, int(type), id)
    )
    return {"code": 200, "msg": 'success', "data": prompt_result}


# 删除个人提示词
@router.post("/delete_prompt")
async def delete_prompt(
        request: Request,
        id: int = Body(..., embed=True, description="提示词id")
):
    prompt_result = sqlite_execute("DELETE FROM `prompt` WHERE id=?", (id,))
    return {"code": 200, "msg": 'success', "data": prompt_result}


# 获取全部提示词分类
@router.post("/get_all_prompt_type")
async def get_all_prompt_type(
        request: Request,
        user_id: int = Body(..., embed=True, description="用户id")
):
    result = sqlite_execute("SELECT * FROM `prompt_type` WHERE user_id=?", (user_id,))
    return {"code": 200, "msg": 'success', "data": result}


# 获取当前用户标签列表
@router.post("/get_label")
async def get_label(
        request: Request,
        user_id: int = Body(..., embed=True, description="用户id"),
):
    result = sqlite_execute("SELECT * FROM `label` WHERE user_id=?", (user_id,))
    return {"code": 200, "msg": 'success', "data": result}


# 添加个人标签
@router.post("/add_label")
async def add_label(
        request: Request,
        user_id: int = Body(..., embed=True, description="用户id"),
        label_name: str = Body(..., embed=True, description="标签名称"),
):
    label_result = sqlite_execute(
        "INSERT INTO `label` (user_id, label_name) VALUES (?, ?)",
        (user_id, label_name)
    )
    return {"code": 200, "msg": 'success', "data": label_result}


@router.post("/delete_label")
async def delete_label(
        request: Request,
        id: int = Body(..., embed=True, description="标签id")
):
    label_result = sqlite_execute("DELETE FROM `label` WHERE id=?", (id,))
    return {"code": 200, "msg": 'success', "data": label_result}


# 更改用户密码接口
@router.post("/change_password")
async def change_password(
        request: Request,
        user_id: int = Body(..., embed=True, description="用户id"),
        old_password: str = Body(..., embed=True, description="旧密码"),
        new_password: str = Body(..., embed=True, description="新密码"),
):
    """
    修改用户密码
    """
    # 校验旧密码
    user_info = sqlite_execute(
        "SELECT id FROM user WHERE id=? AND passwd=?",
        (user_id, old_password)
    )
    if not user_info:
        return {"code": 400, "msg": "旧密码错误"}

    # 更新新密码
    try:
        sqlite_execute(
            "UPDATE user SET passwd=? WHERE id=?",
            (new_password, user_id)
        )
        return {"code": 200, "msg": "密码修改成功"}
    except Exception as e:
        return {"code": 500, "msg": f"修改失败: {str(e)}"}




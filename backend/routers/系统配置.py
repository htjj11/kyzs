'''
系统认证相关接口
'''

from fastapi import APIRouter, Request, Body
from core.sqlLiteExec import sqlite_execute
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import urllib.parse
from datetime import datetime, timedelta
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

        user_id = user_result[0]['id']
        rag_bind = sqlite_execute(
            "SELECT ragflow_id FROM `个人知识库绑定` WHERE 用户id=?",
            (user_id,),
        )
        ragflow_id = rag_bind[0]['ragflow_id'] if rag_bind else None

        return {
            "code": 200,
            "msg": 'success',
            "data": {
                "user_id": user_id,
                "user_name": username,
                "permission": permission_list,
                "ragflow_id": ragflow_id,
            },
        } 

    else:
        return {"code": 400, "msg": 'fail', "data": {"msg": "用户名或密码错误"}}

#单点登录校验
@router.get('/sso_login')
async def sso_login(request: Request, tk: str):
    """
    单点登录接口：接收外部系统通过 ?tk=xxx 传入的 AES 加密串
    加密内容格式：username=xxx&type=bgpt&date=yyyy-MM-dd HH:mm:ss
    """
    SSO_KEY = "zrykZRYKtT00.778"  # 16 位共同密鑰
    SSO_TYPE = "bgpt"               # 约定类型标识
    TIME_WINDOW = 30                # 时间窗口（分钟）

    # 1. URL 解码（处理 %2B 等编码字符）
    print("[SSO] 步骤1: URL解码, 原始tk=", tk)
    try:
        decoded_tk = urllib.parse.unquote(tk)
        print("[SSO] 步骤1完成: decoded_tk=", decoded_tk)
    except Exception as e:
        print("[SSO] 步骤1失败: URL解码异常", e)
        return {"code": 400, "msg": "tk 参数 URL 解码失败"}

    # 2. Base64 解码 + AES/ECB/PKCS5 解密
    print("[SSO] 步骤2: AES解密...")
    try:
        cipher_bytes = base64.b64decode(decoded_tk)
        cipher = AES.new(SSO_KEY.encode("utf-8"), AES.MODE_ECB)
        plain_bytes = unpad(cipher.decrypt(cipher_bytes), AES.block_size)
        plain_text = plain_bytes.decode("utf-8")
        print("[SSO] 步骤2完成: 明文=", plain_text)
    except Exception as e:
        print("[SSO] 步骤2失败: 解密异常", e)
        return {"code": 400, "msg": f"解密失败：{str(e)}"}

    # 3. 解析参数 username / type / date
    print("[SSO] 步骤3: 解析参数...")
    try:
        params = dict(item.split("=", 1) for item in plain_text.split("&") if "=" in item)
        username = params.get("username", "").strip()
        sso_type = params.get("type", "").strip()
        date_str = params.get("date", "").strip()
        print(f"[SSO] 步骤3完成: username={username}, type={sso_type}, date={date_str}")
    except Exception as e:
        print("[SSO] 步骤3失败: 解析异常", e)
        return {"code": 400, "msg": "加密内容格式错误"}

    # 4. 校验 type 字段
    print(f"[SSO] 步骤4: 校验type, 期望={SSO_TYPE}, 实际={sso_type}")
    if sso_type != SSO_TYPE:
        print("[SSO] 步骤4失败: type不匹配")
        return {"code": 400, "msg": f"类型参数不匹配，期望 {SSO_TYPE}，实际 {sso_type}"}
    print("[SSO] 步骤4完成: type校验通过")

    # 5. 校验时间窗口（正负 30 分钟）
    print(f"[SSO] 步骤5: 校验时间窗口, date_str={date_str}")
    try:
        token_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        diff_seconds = abs((now - token_time).total_seconds())
        print(f"[SSO] 步骤5: token时间={token_time}, 当前时间={now}, 差值秒={diff_seconds}, 阈值={TIME_WINDOW * 60}")
        if diff_seconds > TIME_WINDOW * 60:
            print("[SSO] 步骤5失败: token已过期")
            return {"code": 400, "msg": "token 已过期，请重新登录"}
        print("[SSO] 步骤5完成: 时间窗口校验通过")
    except Exception as e:
        print("[SSO] 步骤5失败: 时间格式异常", e)
        return {"code": 400, "msg": f"时间格式错误，期望 yyyy-MM-dd HH:mm:ss，实际：{date_str}"}

    # 6. 根据 username 查询用户（免密，不校验密码）
    print(f"[SSO] 步骤6: 查询用户, username={username}")
    user_result = sqlite_execute(
        "SELECT id FROM user WHERE name=?",
        (username,)
    )
    print(f"[SSO] 步骤6: 查询结果={user_result}")
    if not user_result:
        print(f"[SSO] 步骤6失败: 用户不存在, username={username}")
        return {"code": 400, "msg": f"用户 '{username}' 不存在"}

    user_id = user_result[0]['id']
    print(f"[SSO] 步骤6完成: user_id={user_id}")

    # 7. 获取用户权限
    print(f"[SSO] 步骤7: 查询用户权限, user_id={user_id}")
    permission_result = sqlite_execute(
        "SELECT permission FROM user_permissions WHERE user_id=?",
        (user_id,)
    )
    permission_list = [item['permission'] for item in permission_result] if permission_result else []
    print(f"[SSO] 步骤7完成: permissions={permission_list}")

    # 8. 获取 ragflow 绑定
    print(f"[SSO] 步骤8: 查询ragflow绑定, user_id={user_id}")
    rag_bind = sqlite_execute(
        "SELECT ragflow_id FROM `个人知识库绑定` WHERE 用户id=?",
        (user_id,)
    )
    ragflow_id = rag_bind[0]['ragflow_id'] if rag_bind else None
    print(f"[SSO] 步骤8完成: ragflow_id={ragflow_id}")

    print("[SSO] 全部步骤完成, 返回成功")
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "user_id": user_id,
            "user_name": username,
            "permission": permission_list,
            "ragflow_id": ragflow_id,
        },
    }


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


# 超级管理员

# ==================== 用户权限管理接口（统一入口） ====================

@router.post("/user_permission")
async def user_permission(
        request: Request,
        action: str = Body(..., embed=True, description="操作类型：get / add / set / update / delete / delete_all"),
        user_id: int = Body(..., embed=True, description="发起请求的用户id"),
        user_name: str = Body(..., embed=True, description="要操作权限的目标用户名称"),
        permission: str = Body(None, embed=True, description="权限标识，如 document:delete（add/update/delete 时必填）"),
        new_permission: str = Body(None, embed=True, description="新权限标识（update 时必填）"),
        permissions: list = Body(None, embed=True, description="权限列表（set 时必填），如 ['document:delete']"),
):
    """
    用户权限统一管理接口，通过 action 区分操作：

    - user_id     : 发起请求的操作人 id（鉴权备用）
    - user_name   : 要操作权限的目标用户名，接口会自动从 user 表查出对应 id
    - get         : 查询该用户所有权限
    - add         : 新增单条权限（需传 permission）
    - set         : 批量覆盖设置权限（需传 permissions 列表）
    - update      : 修改某条权限（需传 permission + new_permission）
    - delete      : 删除单条权限（需传 permission）
    - delete_all  : 清空该用户所有权限
    """

    # ---------- 通过 user_name 查出目标用户 id ----------
    target_user = sqlite_execute(
        "SELECT id FROM user WHERE name=?",
        (user_name,),
        fetch="one"
    )
    if not target_user:
        return {"code": 404, "msg": f"用户 '{user_name}' 不存在", "data": None}
    target_user_id = str(target_user["id"])

    # ---------- get ----------
    if action == "get":
        result = sqlite_execute(
            "SELECT user_id, permission FROM user_permissions WHERE user_id=?",
            (target_user_id,)
        )
        return {"code": 200, "msg": "success", "data": result}

    # ---------- add ----------
    elif action == "add":
        if not permission:
            return {"code": 400, "msg": "add 操作需传 permission", "data": None}
        exists = sqlite_execute(
            "SELECT 1 FROM user_permissions WHERE user_id=? AND permission=?",
            (target_user_id, permission)
        )
        if exists:
            return {"code": 400, "msg": "该权限已存在", "data": None}
        sqlite_execute(
            "INSERT INTO user_permissions (user_id, permission) VALUES (?, ?)",
            (target_user_id, permission), fetch="none"
        )
        return {"code": 200, "msg": "权限添加成功", "data": None}

    # ---------- set ----------
    elif action == "set":
        if permissions is None:
            return {"code": 400, "msg": "set 操作需传 permissions 列表", "data": None}
        sqlite_execute(
            "DELETE FROM user_permissions WHERE user_id=?",
            (target_user_id,), fetch="none"
        )
        for perm in permissions:
            sqlite_execute(
                "INSERT OR IGNORE INTO user_permissions (user_id, permission) VALUES (?, ?)",
                (target_user_id, str(perm)), fetch="none"
            )
        return {"code": 200, "msg": "权限设置成功", "data": None}

    # ---------- update ----------
    elif action == "update":
        if not permission or not new_permission:
            return {"code": 400, "msg": "update 操作需传 permission 和 new_permission", "data": None}
        exists = sqlite_execute(
            "SELECT 1 FROM user_permissions WHERE user_id=? AND permission=?",
            (target_user_id, permission)
        )
        if not exists:
            return {"code": 400, "msg": "旧权限不存在", "data": None}
        new_exists = sqlite_execute(
            "SELECT 1 FROM user_permissions WHERE user_id=? AND permission=?",
            (target_user_id, new_permission)
        )
        if new_exists:
            return {"code": 400, "msg": "新权限已存在，无需修改", "data": None}
        sqlite_execute(
            "UPDATE user_permissions SET permission=? WHERE user_id=? AND permission=?",
            (new_permission, target_user_id, permission), fetch="none"
        )
        return {"code": 200, "msg": "权限修改成功", "data": None}

    # ---------- delete ----------
    elif action == "delete":
        if not permission:
            return {"code": 400, "msg": "delete 操作需传 permission", "data": None}
        exists = sqlite_execute(
            "SELECT 1 FROM user_permissions WHERE user_id=? AND permission=?",
            (target_user_id, permission)
        )
        if not exists:
            return {"code": 400, "msg": "该权限不存在", "data": None}
        sqlite_execute(
            "DELETE FROM user_permissions WHERE user_id=? AND permission=?",
            (target_user_id, permission), fetch="none"
        )
        return {"code": 200, "msg": "权限删除成功", "data": None}

    # ---------- delete_all ----------
    elif action == "delete_all":
        sqlite_execute(
            "DELETE FROM user_permissions WHERE user_id=?",
            (target_user_id,), fetch="none"
        )
        return {"code": 200, "msg": "已清空该用户所有权限", "data": None}

    else:
        return {"code": 400, "msg": f"未知 action：{action}，可选值：get / add / set / update / delete / delete_all", "data": None}

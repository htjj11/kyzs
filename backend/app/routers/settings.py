'''
设置接口
'''
from app.core.database import db as kyzs_sql
from fastapi import APIRouter, Request, Body

router = APIRouter(
    prefix="/get_setting",
    tags=["获取所有与系统相关设置"],
)


@router.post("/get_all_label")
async def get_all_label(
    request: Request,
    user_id: int = Body(..., embed=True, description="用户id")
):
    res = kyzs_sql.mysql_exec("SELECT * FROM `label` WHERE user_id=%s", (user_id,))
    return {"code": 200, "msg": 'success', "data": res}


@router.post("/get_all_prompt")
async def get_all_prompt(
    request: Request,
    user_id: int = Body(..., embed=True, description="用户id")
):
    result = kyzs_sql.mysql_exec("SELECT * FROM `prompt` WHERE user_id=%s", (user_id,))
    return {"code": 200, "msg": 'success', "data": result}


@router.post("/add_prompt")
async def add_prompt(
    request: Request,
    user_id: int = Body(..., embed=True, description="用户id"),
    name: str = Body(..., embed=True, description="提示词名称"),
    text: str = Body(..., embed=True, description="提示词类型id"),
    type: int = Body(..., embed=True, description="提示词内容")
):
    prompt_result = kyzs_sql.mysql_exec(
        "INSERT INTO `prompt` (user_id, name, text, type) VALUES (%s, %s, %s, %s)",
        (user_id, name, text, int(type))
    )
    return {"code": 200, "msg": 'success', "data": prompt_result}


@router.post("/update_prompt")
async def update_prompt(
    request: Request,
    name: str = Body(..., embed=True, description="提示词名称"),
    text: str = Body(..., embed=True, description="提示词类型id"),
    type: int = Body(..., embed=True, description="提示词内容"),
    id: int = Body(..., embed=True, description="提示词id")
):
    prompt_result = kyzs_sql.mysql_exec(
        "UPDATE `prompt` SET name=%s, text=%s, type=%s WHERE id=%s",
        (name, text, int(type), id)
    )
    return {"code": 200, "msg": 'success', "data": prompt_result}


@router.post("/delete_prompt")
async def delete_prompt(
    request: Request,
    id: int = Body(..., embed=True, description="提示词id")
):
    prompt_result = kyzs_sql.mysql_exec("DELETE FROM `prompt` WHERE id=%s", (id,))
    return {"code": 200, "msg": 'success', "data": prompt_result}


@router.post("/get_all_prompt_type")
async def get_all_prompt_type(
    request: Request,
    user_id: int = Body(..., embed=True, description="用户id")
):
    result = kyzs_sql.mysql_exec("SELECT * FROM `prompt_type` WHERE user_id=%s", (user_id,))
    return {"code": 200, "msg": 'success', "data": result}


@router.post("/get_label")
async def get_label(
    request: Request,
    user_id: int = Body(..., embed=True, description="用户id"),
):
    result = kyzs_sql.mysql_exec("SELECT * FROM `label` WHERE user_id=%s", (user_id,))
    return {"code": 200, "msg": 'success', "data": result}


@router.post("/add_label")
async def add_label(
    request: Request,
    user_id: int = Body(..., embed=True, description="用户id"),
    label_name: str = Body(..., embed=True, description="标签名称"),
):
    label_result = kyzs_sql.mysql_exec(
        "INSERT INTO `label` (user_id, label_name) VALUES (%s, %s)",
        (user_id, label_name)
    )
    return {"code": 200, "msg": 'success', "data": label_result}


@router.post("/delete_label")
async def delete_label(
    request: Request,
    id: int = Body(..., embed=True, description="标签id")
):
    label_result = kyzs_sql.mysql_exec("DELETE FROM `label` WHERE id=%s", (id,))
    return {"code": 200, "msg": 'success', "data": label_result}

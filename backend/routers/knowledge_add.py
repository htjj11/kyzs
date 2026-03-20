'''
增加（收藏）信息接口
'''
from fastapi import APIRouter, Request, Body
from services.literature_service import (
    add_article_to_knowledge,
    add_patent_to_knowledge,
    add_online_infomation_to_knowledge,
    add_mycontent_to_knowledge,
    add_mycontent_file_to_knowledge,
)

router = APIRouter(
    prefix="/add_to_knowledge",
    tags=["收藏接口"],
)


@router.post('/add_knowledge')
async def add_knowledge(
    request: Request,
    data_dict: dict = Body(..., embed=True, description="收藏信息"),
    label_id: int = Body(..., embed=True, description="收藏标签id"),
    user_id: int = Body(..., embed=True, description="用户id"),
    type_id: int = Body(..., embed=True, description="收藏类型(1是文献；2专利；3网络信息；4自定义信息)"),
):
    """
    添加收藏接口，将收藏信息添加到数据库中，现判定type属于哪一类，再执行对应方法
    """
    print(f'用户请求类型{type_id}收藏')
    if type_id == 1:
        add_result = add_article_to_knowledge(article_data=data_dict, label_id=label_id, user_id=user_id)
    elif type_id == 2:
        add_result = add_patent_to_knowledge(patent_data=data_dict, label_id=label_id, user_id=user_id)
    elif type_id == 3:
        add_result = add_online_infomation_to_knowledge(online_infomation=data_dict, label_id=label_id, user_id=user_id)
    elif type_id == 4:
        add_result = add_mycontent_to_knowledge(content=data_dict['content_string'], title=data_dict['title_string'], label_id=label_id, user_id=user_id)
    elif type_id == 5:
        # 前端传入格式: data_dict = { "data": [ {file1}, {file2}, ... ] }
        file_list = data_dict.get('data', [])
        if not file_list:
            return {"code": 400, "msg": "未传入文件数据", "data": None}
        for idx, file_item in enumerate(file_list):
            print(f"正在添加第 {idx + 1}/{len(file_list)} 个文件: {file_item.get('title_string', '未知')}")
            add_result = add_mycontent_file_to_knowledge(
                file_base64_string=file_item['file_base64_string'],
                file_extension=file_item['file_extension'],
                title=file_item['title_string'],
                label_id=label_id,
                user_id=user_id
            )
            if add_result['code'] != 200:
                return add_result
        return {"code": 200, "msg": "success", "data": None}
    else:
        return {"code": 500, "msg": "收藏类型错误"}

    if add_result['code'] == 200:
        return {"code": 200, "msg": "success", "data": None}
    return add_result

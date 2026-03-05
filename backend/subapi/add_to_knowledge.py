'''
增加（收藏）信息接口

'''
from fastapi import APIRouter, Request,Body
from api.api_bg import *

router = APIRouter(
    prefix="/add_to_knowledge",        # 给该模块统一加前缀
    tags=["收藏接口"],       # 接口分组
)

#添加收藏
@router.post('/add_knowledge')
async def add_knowledge(
    request: Request,  # 添加 Request 对象以获取请求信息
    data_dict: dict = Body(..., embed=True, description="收藏信息"),
    label_id:int = Body(..., embed=True, description="收藏标签id"),
    user_id:int = Body(..., embed=True, description="用户id"),
    type_id: int = Body(..., embed=True, description="收藏类型(1是文献；2专利；3网络信息；4自定义信息)"),
):
    """
    添加收藏接口，将收藏信息添加到数据库中，现判定type属于哪一类，再执行对应方法
    :param request: Request 对象，包含请求信息
    :param data_dict: 收藏信息
    :param type_id: 收藏类型
    :return:
    """ 
    print(f'用户请求类型{type_id}收藏')
    if type_id == 1:
        add_result = add_article_to_knowledge(article_data=data_dict,label_id=label_id,user_id=user_id)
    elif type_id == 2:
        add_result = add_patent_to_knowledge(patent_data=data_dict,label_id=label_id,user_id=user_id)
    elif type_id == 3:
        add_result = add_online_infomation_to_knowledge(online_infomation=data_dict,label_id=label_id,user_id=user_id)
    elif type_id == 4:
        add_result = add_mycontent_to_knowledge(content=data_dict['content_string'],title=data_dict['title_string'],label_id=label_id,user_id=user_id)
    elif type_id == 5:
        
        add_result = add_mycontent_file_to_knowledge(file_base64_string=data_dict['file_base64_string'],file_extension=data_dict['file_extension'],title=data_dict['title_string'],label_id=label_id,user_id=user_id)
    else:
        return {"code": 500, "msg": "收藏类型错误"}
    
    #根据插入情况给前端返回不同的结果
    if add_result['code'] == 200:
        return {"code": 200, "msg": "success", "data": None}
    return add_result

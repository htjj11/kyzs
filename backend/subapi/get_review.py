'''
报告接口

'''
import asyncio
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor()  # 全局线程池，避免重复创建

from api.sql_role import kyzs_sql
from fastapi import APIRouter, Request,Body
from api.api_bg import *

router = APIRouter(
    prefix="/get_review",        # 给该模块统一加前缀   
    tags=["获取所有综述相关设置"],       # 接口分组
)


'''
review_record 报告表结构
CREATE TABLE `review_records` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  `title` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '报告的主题',
  `completion_status` tinyint(1) NOT NULL DEFAULT '0' COMMENT '完成情况，0表示未完成，1表示已完成',
  `review_body` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '综述正文',
  `user_id` int DEFAULT NULL COMMENT '绑定的用户id',
  `label_id` int DEFAULT NULL COMMENT '绑定的标签id',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=474 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='综述记录表';
'''

@router.post("/create_review")
async def create_review(
    request:Request,
    user_id:int = Body(...,embed=True,description="用户id"),
    title:str = Body(...,embed=True,description="报告的主题"),
):
    """
    创建一个报告
    :return: 报告id
    """
    sql_sentence = f"""
    INSERT INTO `review_records` (title, completion_status, review_body, user_id)
    VALUES ('{title}', 0, '请从此处开始编辑', {user_id});
    """
    res = kyzs_sql.mysql_exec(sql_sentence)
    return {"code":200,"msg":'success',"data":res}

@router.post("/create_review_by_template")
async def create_review_by_template(
    request:Request,
    user_id:int = Body(...,embed=True,description="用户id"),
    title:str = Body(...,embed=True,description="报告的主题"),
    template_id:int = Body(...,embed=True,description="绑定的模板id")
):
    """
    修改报告完成情况
    :return: 报告id
    """
    # 检查模板是否存在
    sql_sentence = f"""
    SELECT * FROM `review_template` WHERE id={template_id};
    """
    template_content = kyzs_sql.mysql_exec(sql_sentence)[0]['content']


    sql_sentence = f"""
    INSERT INTO `review_records` (title, completion_status, review_body, user_id,label_id)
    VALUES ('{title}', 0, '{template_content}', {user_id},{template_id});
    """
    res = kyzs_sql.mysql_exec(sql_sentence)
    return {"code":200,"msg":'success',"data":res}



@router.post("/delete_review")
async def delete_review(
    request:Request,
    review_id:int = Body(...,embed=True,description="报告id")
):
    """
    删除报告
    :return: 报告id
    """
    sql_sentence = f"""
    DELETE FROM `review_records` WHERE id={review_id};  
    """
    res = kyzs_sql.mysql_exec(sql_sentence)
    return {"code":200,"msg":'success',"data":res}



@router.post("/get_all_review")
async def get_all_review(
    request:Request,
    user_id:int = Body(...,embed=True,description="用户id")
):
    """
    获取当前用户id下的报告
    :return: 所有报告
    """
    sql_sentence = f"""
    SELECT * FROM `review_records` where user_id={user_id}
    """
    res = kyzs_sql.mysql_exec(sql_sentence)
    return {"code":200,"msg":'success',"data":res}


@router.post("/get_review_base64")
async def get_review_detail(
    request:Request,
    review_id:int = Body(...,embed=True,description="报告id")
):
    """
    获取当前报告id下的base64编码
    :return: 报告base64编码 
    """
    base64_string = generate_word_api(review_id)

    return {"code":200,"msg":'success',"data":base64_string}    



@router.post("/get_review_fuwenben_base64")
async def get_review_fuwenben_base64(
    request:Request,
    review_id:int = Body(...,embed=True,description="报告id")
):
    """
    获取当前报告id下的base64编码（富文本）
    :return: 报告base64编码 
    """
    base64_string = generate_fuwenben_word_api(review_id)

    return {"code":200,"msg":'success',"data":base64_string}    




@router.post('/modify_review')
async def modify_review(
    request: Request,  # 添加 Request 对象以获取请求信息
    review_id: int = Body(..., embed=True, description="记录id"),
    start_position: int = Body(..., embed=True, description="目标文本起始位置"),
    end_position: int = Body(..., embed=True, description="目标文本结束位置"),
    replaced_text: str = Body(..., embed=True, description="替换文本"),
):
    """
    修改综述生成记录
    :return:
    """
    print(f"用户请求 IP: {request.client.host}，记录id：{review_id}，目标文本起始位置：{start_position}，目标文本结束位置：{end_position}，替换文本：{replaced_text}")
    response =   modify_summary_api(review_id,start_position,end_position,replaced_text)
    if response:    
        return {"code": 200, "msg": "success", "data": None}
    return 0


# 新增接口，用于修改综述，直接采取全文替换方式
@router.post("/modify_review_new")
async def modify_review_new(
    request: Request,  # 添加 Request 对象以获取请求信息
    review_id: int = Body(..., embed=True, description="记录id"),
    review_body: str = Body(..., embed=True, description="综述正文"),
):
    """
    修改综述生成记录完成情况
    :return:
    """
    print(f"用户请求 IP: {request.client.host}，记录id：{review_id}，综述正文：{review_body}")
    response = modify_review_new_api(review_id,review_body)
    if response:    
        return {"code": 200, "msg": "success", "data": None}
    return 0



from concurrent.futures import ThreadPoolExecutor

# 创建线程池，避免重复创建
executor = ThreadPoolExecutor()

@router.post('/get_summary_by_ai')
async def get_summary_by_ai(
    request: Request,  # 添加 Request 对象以获取请求信息
    knowledge_ids: list[int] = Body(..., embed=True, description="知识库id列表"),
    prompt_ids: list[int] = Body(..., embed=True, description="提示词id列表"),
    user_need: str = Body(..., embed=True, description="用户需求字符串"),
):
    """
    传入参考知识库id列表,提示词id列表,用户需求字符串

    :return: 大模型生成的文本
    """
    # 从数据库中获取知识库内容
    sql = f"""
        SELECT content FROM knowledgebase
        WHERE id IN ({','.join(map(str, knowledge_ids))})
    """
    knowledge_content = kyzs_sql.mysql_exec(sql)
    # 从数据库中获取提示词内容
    sql = f"""
        SELECT text FROM prompt
        WHERE id IN ({','.join(map(str, prompt_ids))})
    """
    prompt_content = kyzs_sql.mysql_exec(sql)
    # 合并知识库内容（添加空校验）
    knowledge_content = '\n'.join([item['content'] for item in knowledge_content if item.get('content')]) if knowledge_content else ''
    # 合并提示词内容（添加空校验）
    prompt_content = '\n'.join([item['text'] for item in prompt_content if item.get('text')]) if prompt_content else ''

    # 调用大模型生成文本
    prompt =f'''    
    知识库内容：
    {knowledge_content}
    格式\内容要求：
    {prompt_content}
    用户需求：
    {user_need}
    请你按照需求,直接回复用户,不需要多余的解释
    '''
    print(prompt)
    
    # 使用线程池异步执行耗时的大模型调用，避免阻塞其他接口
    summary = await asyncio.get_event_loop().run_in_executor(
        executor, 
        siliconflow_deepseek_answer, 
        prompt
    )

    return {"code":200,"msg":"success","data":summary}    


'''
报告模板表
CREATE TABLE `review_template` (
  `id` int NOT NULL,
  `name` varchar(255) DEFAULT NULL COMMENT '报告模板名称',
  `content` text COMMENT '报告模板正文',
  `user_id` int DEFAULT NULL COMMENT '绑定到每个用户的id',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

'''
################报告模版相关接口###############


@router.post("/get_all_template")
async def get_all_template(
    request:Request,
    user_id:int = Body(...,embed=True,description="用户id")
):
    """
    获取当前用户id下的报告模板
    :return: 所有报告模板
    """
    sql_sentence = f"""
    SELECT * FROM `review_template` 
    """
    res = kyzs_sql.mysql_exec(sql_sentence)
    return {"code":200,"msg":'success',"data":res}







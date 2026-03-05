import asyncio
import requests
import json
import uuid
from fastapi import APIRouter, Request, Body
from fastapi.responses import StreamingResponse
from api.api_chat import *



# 创建路由对象
router = APIRouter(
    prefix="/llm",        # 给该模块统一加前缀
    tags=["LLM对话接口"],    # 接口分组
)

@router.post('/stream_chat')
def stream_chat(
    request: Request,
    message: str = Body(..., embed=True, description="用户的问题")
):
    """
    流式对话接口
    :param request: Request对象，包含请求信息
    :param message: 用户的问题
    :return: 流式响应
    """
    print(f"\033[32m用户请求 IP: {request.client.host}，问题：{message}\033[0m")
    
    try:
        # 获取生成器对象
        generator = stream_chat_handler(message)
        
        # 创建并返回流式响应
        # 注意：由于我们在生成器中已经正确格式化了响应内容，这里使用text/event-stream
        return StreamingResponse(
            generator,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    except Exception as e:
        print(f"\033[31m流式响应处理失败: {str(e)}\033[0m")
        
        # 发生异常时，创建一个错误响应生成器
        def error_generator():
            error_msg = {
                "uuid": str(uuid.uuid4()),
                "type": "error",
                "error": True,
                "message": f"流式响应处理失败: {str(e)}"
            }
            error_chunk = f"data: {json.dumps(error_msg)}\n\n".encode('utf-8')
            yield error_chunk
        
        return StreamingResponse(
            error_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )

@router.post('/simple_chat')
def simple_chat(
    message: str = Body(..., embed=True, description="用户的问题")
):
    """
    简单对话接口（非流式，仅用于测试）
    :param message: 用户的问题
    :return: 完整的对话响应
    """
    # 配置LLM服务器信息
    llm_ip = "http://localhost:3001"
    anythingLLMWorkSpace = "kyzs"
    thread_id = "identifier-to-partition-chats-by-external-id"
    anythingLLMKey = "Bearer DKNAE05-JDBMAEN-M2R3BA5-CETY1F2"
    
    # 构建请求URL
    llm_url = llm_ip + f"/api/v1/workspace/{anythingLLMWorkSpace}/thread/{thread_id}/stream-chat"
    
    # 设置请求头
    headers = {
        "Authorization": anythingLLMKey
    }
    
    # 设置请求体
    data = {
        "message": message,
        "mode": "chat"
    }
    
    try:
        # 发送POST请求
        response = requests.post(llm_url, json=data, headers=headers)
        response.raise_for_status()
        
        # 处理响应内容
        content = response.text
        results = []
        
        # 处理可能的text/event-stream格式响应
        if response.headers.get('Content-Type') == 'text/event-stream':
            # 分割每一行
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # 移除data:前缀
                if line.startswith('data: '):
                    line = line.replace('data: ', '')
                
                try:
                    data_json = json.loads(line)
                    # 添加thread_id字段
                    data_json['thread_id'] = thread_id
                    results.append(data_json)
                except json.JSONDecodeError:
                    continue
        else:
            # 尝试直接解析整个响应
            try:
                data_json = json.loads(content)
                # 添加thread_id字段
                data_json['thread_id'] = thread_id
                results.append(data_json)
            except json.JSONDecodeError:
                # 如果解析失败，按行处理
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data_json = json.loads(line)
                        # 添加thread_id字段
                        data_json['thread_id'] = thread_id
                        results.append(data_json)
                    except json.JSONDecodeError:
                        continue
        
        return {
            "code": 200,
            "msg": "success",
            "data": results,
            "thread_id": thread_id
        }
    except requests.RequestException as e:
        print(f"\033[31m简单对话请求出错: {str(e)}\033[0m")
        return {
            "code": 500,
            "msg": f"请求出错: {str(e)}",
            "data": None,
            "thread_id": thread_id
        }
    except Exception as e:
        print(f"\033[31m简单对话请求发生未知错误: {str(e)}\033[0m")
        return {
            "code": 500,
            "msg": f"发生未知错误: {str(e)}",
            "data": None,
            "thread_id": thread_id
        }


@router.post('/add_knowledge_to_anythingllm')
def add_knowledge_to_anythingllm(
    user_id: int = Body(..., embed=True, description="用户ID"),
    knowledge_id: int = Body(..., embed=True, description="知识ID"),
    folder_id: int = Body(..., embed=True, description="文件夹ID"),
):
    """
    将知识库文本写入到大模型知识库
    :param user_id: 用户ID
    :param knowledge_id: 知识库ID
    :return: 成功或失败
    """
    result = all_text_to_db(user_id,knowledge_id,folder_id)
    if result['code'] == 200:
        return {
            "code": 200,
            "msg": "success",
            "data": None,
        }
    else:
        return {
            "code": 500,
            "msg": result['msg'],
            "data": None,
        }



@router.post('/get_all_anything_db')
def get_all_anything_db(
    user_id: int = Body(..., embed=True, description="用户ID")
):
    """
    获取所有anything_db中的数据
    :param user_id: 用户ID
    :return: 所有数据的列表
    """
    result = get_all_anything_db_api(user_id)

    return {
        "code": 200,
        "msg": "success",
        "data": result,
    }





@router.post('/delete_anything_db')
def delete_anything_db(
    id: int = Body(..., embed=True, description="数据ID")
):
    """
    删除所有anything_db中的数据
    :param id: 数据ID
    :return: 成功或失败
    """
    result = delete_anything_db_api(id)
    if result:
        return {
            "code": 200,
            "msg": "success",
            "data": None,
        }
    else:
        return {
            "code": 500,
            "msg": "fail",
            "data": None,
        }
 


@router.post('/get_public_anything_db')
def get_public_anything_db_by_folder(
    user_id: int = Body(..., embed=True, description="用户ID"),
):
    """
    获取公共知识库下所有数据
    :param user_id: 用户ID
    :return: 所有公共数据的列表
    """
    result = get_public_anything_db_api()

    return {
        "code": 200,
        "msg": "success",
        "data": result,
    }

@router.post('/get_all_folders')
def get_all_folders(
    user_id: int = Body(..., embed=True, description="用户ID")
):
    """
    获取所有文件夹
    :param user_id: 用户ID
    :return: 所有文件夹的列表
    """
    result = get_all_folders_api()

    return {
        "code": 200,
        "msg": "success",
        "data": result,
    }

@router.post('/get_anything_db_by_id')
def get_anything_db_by_id(
    id: int = Body(..., embed=True, description="数据ID")
):
    """
    根据ID获取anything_db中的数据
    :param id: 数据ID
    :return: 对应数据的字典
    """
    result = get_anythingdb_by_id_api(id)
    if result:
        return {
            "code": 200,
            "msg": "success",
            "data": result,
        }
    else:
        return {
            "code": 500,
            "msg": "fail",
            "data": None,
        }
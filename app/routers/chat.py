import asyncio
import requests
import json
import uuid
from fastapi import APIRouter, Request, Body
from fastapi.responses import StreamingResponse
from app.config import settings
from app.services.chat_service import (
    stream_chat_handler,
    all_text_to_db,
    get_all_anything_db_api,
    delete_anything_db_api,
    get_public_anything_db_api,
    get_all_folders_api,
    get_anythingdb_by_id_api,
)

router = APIRouter(
    prefix="/llm",
    tags=["LLM对话接口"],
)


@router.post('/stream_chat')
def stream_chat(
    request: Request,
    message: str = Body(..., embed=True, description="用户的问题")
):
    """
    流式对话接口
    """
    print(f"\033[32m用户请求 IP: {request.client.host}，问题：{message}\033[0m")

    try:
        generator = stream_chat_handler(message)

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
    """
    llm_ip = settings.anythingllm_base_url
    anythingLLMWorkSpace = settings.anythingllm_workspace
    thread_id = "identifier-to-partition-chats-by-external-id"
    anythingLLMKey = f"Bearer {settings.anythingllm_api_key}"

    llm_url = llm_ip + f"/api/v1/workspace/{anythingLLMWorkSpace}/thread/{thread_id}/stream-chat"

    headers = {"Authorization": anythingLLMKey}
    data = {"message": message, "mode": "chat"}

    try:
        response = requests.post(llm_url, json=data, headers=headers)
        response.raise_for_status()

        content = response.text
        results = []

        if response.headers.get('Content-Type') == 'text/event-stream':
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('data: '):
                    line = line.replace('data: ', '')
                try:
                    data_json = json.loads(line)
                    data_json['thread_id'] = thread_id
                    results.append(data_json)
                except json.JSONDecodeError:
                    continue
        else:
            try:
                data_json = json.loads(content)
                data_json['thread_id'] = thread_id
                results.append(data_json)
            except json.JSONDecodeError:
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data_json = json.loads(line)
                        data_json['thread_id'] = thread_id
                        results.append(data_json)
                    except json.JSONDecodeError:
                        continue

        return {"code": 200, "msg": "success", "data": results, "thread_id": thread_id}
    except requests.RequestException as e:
        print(f"\033[31m简单对话请求出错: {str(e)}\033[0m")
        return {"code": 500, "msg": f"请求出错: {str(e)}", "data": None, "thread_id": thread_id}
    except Exception as e:
        print(f"\033[31m简单对话请求发生未知错误: {str(e)}\033[0m")
        return {"code": 500, "msg": f"发生未知错误: {str(e)}", "data": None, "thread_id": thread_id}


@router.post('/add_knowledge_to_anythingllm')
def add_knowledge_to_anythingllm(
    user_id: int = Body(..., embed=True, description="用户ID"),
    knowledge_id: int = Body(..., embed=True, description="知识ID"),
    folder_id: int = Body(..., embed=True, description="文件夹ID"),
):
    """
    将知识库文本写入到大模型知识库
    """
    result = all_text_to_db(user_id, knowledge_id, folder_id)
    if result:
        return {"code": 200, "msg": "success", "data": None}
    else:
        return {"code": 500, "msg": "写入失败", "data": None}


@router.post('/get_all_anything_db')
def get_all_anything_db(
    user_id: int = Body(..., embed=True, description="用户ID")
):
    """
    获取所有anything_db中的数据
    """
    result = get_all_anything_db_api(user_id)
    return {"code": 200, "msg": "success", "data": result}


@router.post('/delete_anything_db')
def delete_anything_db(
    id: int = Body(..., embed=True, description="数据ID")
):
    """
    删除所有anything_db中的数据
    """
    result = delete_anything_db_api(id)
    if result:
        return {"code": 200, "msg": "success", "data": None}
    else:
        return {"code": 500, "msg": "fail", "data": None}


@router.post('/get_public_anything_db')
def get_public_anything_db_by_folder(
    user_id: int = Body(..., embed=True, description="用户ID"),
):
    """
    获取公共知识库下所有数据
    """
    result = get_public_anything_db_api()
    return {"code": 200, "msg": "success", "data": result}


@router.post('/get_all_folders')
def get_all_folders(
    user_id: int = Body(..., embed=True, description="用户ID")
):
    """
    获取所有文件夹
    """
    result = get_all_folders_api()
    return {"code": 200, "msg": "success", "data": result}


@router.post('/get_anything_db_by_id')
def get_anything_db_by_id(
    id: int = Body(..., embed=True, description="数据ID")
):
    """
    根据ID获取anything_db中的数据
    """
    result = get_anythingdb_by_id_api(id)
    if result:
        return {"code": 200, "msg": "success", "data": result}
    else:
        return {"code": 500, "msg": "fail", "data": None}

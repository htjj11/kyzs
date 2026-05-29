import json
import os
import requests

ragflow_api = "http://192.168.137.130/api/v1"
ragflow_token = "ragflow-NO54LNjtXeQk8SPwNX4XhetqLVFmGZCGVXBQcLXo2EQ"
dataset_id = "32d7e35833d411f1839a81bb6c992575"
chat_id = "4a5debf433e711f1839a81bb6c992575"

# 在ragflow中将文件添加至知识库
def upload_to_ragflow(abs_file_path: str) -> dict:
    """
    通过 RAGFlow API 将给定的本地文件上传到指定的知识库
    """
    # 你的 RAGFlow 服务器 API 地址，按照官方 sample 的路径拼接 dataset_id
    url = f"{ragflow_api}/datasets/{dataset_id}/documents"
    
    # 构造请求头，传入 RAGFlow 分配的 API Key
    # 注意：requests 传递 files 时会自动设置带 boundary 的 Content-Type: multipart/form-data，所以不能在 headers 中手动写死
    headers = {
        "Authorization": f"Bearer {ragflow_token}"
    }            
    
    # 构造文件用于上传
    with open(abs_file_path, "rb") as f:
        files = {
            # 表单字段为 file, 传入 (文件名, 文件流对象)
            "file": (os.path.basename(abs_file_path), f)
        }
        # 发送请求
        response = requests.post(url, headers=headers, files=files)
        
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"上传至 RAGFlow 失败: http status {response.status_code}, \n body: {response.text}")

# 将文件内容传入指定id的rag知识库
def upload_to_ragflow_by_id(
    file_path: str,
    rag_dataset_id: str,
    upload_filename: str | None = None,
) -> dict:
    """
    将文件内容传入指定id的rag知识库
    upload_filename: 上传到 RAGFlow 时显示的文件名，默认取本地路径 basename
    """
    url = f"{ragflow_api}/datasets/{rag_dataset_id}/documents"
    headers = {
        "Authorization": f"Bearer {ragflow_token}"
    }
    name = upload_filename or os.path.basename(file_path)
    with open(file_path, "rb") as f:
        files = {
            "file": (name, f)
        }
        response = requests.post(url, headers=headers, files=files)
    if response.status_code == 200:
        return response.json()['data'][0]['id']
    else:
        raise Exception(f"上传至 RAGFlow 失败: http status {response.status_code}, \n body: {response.text}")

 



#触发RAGFlow解析
def start_parsing_document(document_ids: list[str]) -> dict:
    """
    触发 RAGFlow 开始解析及嵌入指定的文档
    """
    url = f"{ragflow_api}/datasets/{dataset_id}/chunks"
    headers = {
        "Authorization": f"Bearer {ragflow_token}",
        "Content-Type": "application/json"
    }            
    data = {
        "document_ids": document_ids
    }
    
    # 传入 json=data 会自动序列化字典并添加 application/json 请求头
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"触发 RAGFlow 文件解析失败: http status {response.status_code}, \n body: {response.text}")


#触发指定知识库的指定文档解析
def start_parsing_document_by_id(rag_dataset_id: str, document_ids: list[str]) -> dict:
    """
    触发指定知识库的指定文档解析        
    """
    url = f"{ragflow_api}/datasets/{rag_dataset_id}/chunks"
    headers = {
        "Authorization": f"Bearer {ragflow_token}",
        "Content-Type": "application/json"
    }
    data = {
        "document_ids": document_ids
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"触发 RAGFlow 文件解析失败: http status {response.status_code}, \n body: {response.text}")


#获取知识库列表
def get_datasets(
    page: int = 1,
    page_size: int = 20,
    orderby: str = "create_time",
    desc: bool = True,
    dataset_name: str = None,
    dataset_id: str = None
) -> dict:
    """
    获取 RAGFlow 中知识库（Dataset）的详细列表信息
    """
    url = f"{ragflow_api}/datasets"
    headers = {
        "Authorization": f"Bearer {ragflow_token}"
    }
    
    # 构造查询参数
    params = {
        "page": page,
        "page_size": page_size,
        "orderby": orderby,
        "desc": str(desc).lower()
    }
    if dataset_name:
        params["name"] = dataset_name
    if dataset_id:
        params["id"] = dataset_id

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"获取 RAGFlow 知识库列表失败: http status {response.status_code}, \n body: {response.text}")

#删除ragflow中的文件
def delete_file_from_ragflow(file_id: str) -> dict:
    """
    从 RAGFlow 中删除指定的文档
    注意：传入的 file_id 必须是 RAGFlow 中的 document ID（字符串格式）
    """
    url = f"{ragflow_api}/datasets/{dataset_id}/documents"
    headers = {
        "Authorization": f"Bearer {ragflow_token}",
        "Content-Type": "application/json"
    }
    data = {
        "ids": [file_id]
    }
    # DELETE 请求携带 json body
    response = requests.delete(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"从 RAGFlow 中删除文件失败: http status {response.status_code}, \n body: {response.text}")


# 删除指定知识库中的指定文档
def delete_file_from_ragflow_by_id(rag_dataset_id: str, file_id: str) -> dict:
    """
    从指定 RAGFlow 知识库中删除文档
    :param rag_dataset_id: 知识库（dataset）ID
    :param file_id: RAGFlow 中的 document ID（字符串格式）
    """
    url = f"{ragflow_api}/datasets/{rag_dataset_id}/documents"
    headers = {
        "Authorization": f"Bearer {ragflow_token}",
        "Content-Type": "application/json"
    }
    data = {
        "ids": [file_id]
    }
    response = requests.delete(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"从 RAGFlow 知识库 {rag_dataset_id} 删除文件失败: "
            f"http status {response.status_code}, \n body: {response.text}"
        )


#建立一个新的知识库，获取其id
def create_new_dataset(dataset_name: str) -> str:
    """
    创建一个新的知识库
    :param dataset_name: 知识库名称
    :return: 创建结果的 id
    """
    url = f"{ragflow_api}/datasets"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ragflow_token}"
    }
    data = {
        "name": dataset_name,
        "embedding_model": "CHANGCHENGEMBEDDING@Ollama",
        "chunk_method": "naive",
        "parser_config": {
            "chunk_token_num": 512,
            "task_page_size": 24
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print(response.json())
        return response.json()['data']['id']
    else:
        raise Exception(f"创建 RAGFlow 数据集失败: http status {response.status_code}, \n body: {response.text}")

#建立一个新的知识库对话，返回对话的chatid
def create_chat_with_dataset(
    dataset_id: str,
    chat_name: str = "My Assistant"
) -> dict:
    """
    基于已有知识库 ID，创建一个 Chat Assistant，返回 chat_id 和嵌入 URL。


    :param api_key:     RAGFlow API Key，例如 "ragflow-xxxxxxxxxxxx"
    :param dataset_id:  已知的知识库 ID
    :param chat_name:   Chat Assistant 名称
    :return: {"chat_id": ..., "embed_url": ..., "iframe": ...}
    """
    url = f"{ragflow_api}/chats"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ragflow_token}",
    }
    payload = {
        "name": chat_name,
        "dataset_ids": [dataset_id],
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(
            f"创建 RAGFlow 对话失败: http status {response.status_code}, \n body: {response.text}"
        )
    result = response.json()
    if result.get("code") != 0:
        raise Exception(f"创建 RAGFlow 对话失败：{result.get('message', result)}")

    chat_id = result["data"]["id"]
    base_url = ragflow_api.split("/api/")[0]
    auth_token = ragflow_token.replace("ragflow-", "", 1)
    embed_url = f"{base_url}/chat/share?shared_id={chat_id}&from=chat&auth={auth_token}"
    iframe_html = (
        f'<iframe src="{embed_url}" width="100%" height="700px" frameborder="0"></iframe>'
    )
    return {
        "chat_id": chat_id,
        "embed_url": embed_url,
        "iframe": iframe_html,
    }


# 从某个知识库检索（base_url、api_key 等使用模块顶部配置）
def search_from_dataset(
    question: str, 
    rag_dataset_id: str | None = None,
    top_k: int = 10,
    similarity_threshold: float = 0.2,
) -> dict:
    """
    直接对指定知识库做语义检索，返回匹配的 chunks。
    :param question: 检索问题
    :param rag_dataset_id: 知识库 ID，默认使用模块配置的 dataset_id
    """
    ds_id = rag_dataset_id or dataset_id
    url = f"{ragflow_api}/retrieval"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ragflow_token}",
    }
    payload = {
        "question": question,
        "dataset_ids": [ds_id],
        "top_n": top_k,
        "similarity_threshold": similarity_threshold,
        "vector_similarity_weight": 0.3,
        "highlight": True,
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(
            f"RAGFlow 检索失败: http status {response.status_code}, \n body: {response.text}"
        )
    result = response.json()
    if result.get("code") != 0:
        raise Exception(f"RAGFlow 检索失败：{result.get('message', result)}")
    return result["data"]


if __name__ == "__main__":
    # test_search_from_dataset()
    print(get_datasets())
    # print(create_new_dataset("test_dataset"))
    # print(upload_to_ragflow_by_id("test.txt", dataset_id))
    # print(search_from_dataset('非商旅平台行程申请审批单','2fde7d98558e11f1a0325562b53a43da'))


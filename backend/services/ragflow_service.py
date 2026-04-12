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


#调用搜索接口，获取ai总结和知识库参考



if __name__ == "__main__":
    # print(get_datasets())
    # upload_to_ragflow("test.txt", "test_dataset")
    # print(delete_file_from_ragflow("71d8e5e633e511f1839a81bb6c992575"))
    for line in chat_with_ragflow("连油数据集成展示装置实施方案？"):
        print(line)
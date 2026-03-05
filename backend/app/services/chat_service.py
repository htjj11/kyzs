import requests
import json
import time
import uuid
from app.core.database import db as kyzs_sql
from app.config import settings

def stream_chat_handler(message: str):
    """
    处理流式对话请求的内部函数
    :param message: 用户的问题
    :return: 流式响应的生成器
    """
    llm_ip = settings.anythingllm_base_url
    anythingLLMWorkSpace = settings.anythingllm_workspace
    thread_id = "identifier-to-partition-chats-by-external-id"
    anythingLLMKey = f"Bearer {settings.anythingllm_api_key}"

    llm_url = llm_ip + f"/api/v1/workspace/{anythingLLMWorkSpace}/stream-chat"

    headers = {
        "Authorization": anythingLLMKey
    }
    
    data = {
        "message": message,
        "mode": "chat"
    }
    
    try:
        response = requests.post(llm_url, json=data, headers=headers, stream=True)
        response.raise_for_status()
        
        def generate():
            for chunk in response.iter_content(chunk_size=50000):
                if chunk:
                    chunk_str = chunk.decode('utf-8')
                    try:
                        if chunk_str.startswith('data: '):
                            chunk_str = chunk_str.replace('data: ', '')
                        
                        data_json = json.loads(chunk_str)

                        if data_json.get('close', True):

                            if 'sources' in data_json and isinstance(data_json['sources'], list):
                                for source in data_json['sources']:
                                    if isinstance(source, dict) and 'id' in source:
                                        try:
                                            published = source['published']
                                            sql = f"SELECT text_title,user_id FROM anything_db WHERE publish_date = '{published}'"
                                            result = kyzs_sql.mysql_exec(sql)
                                            user_id = result[0]['user_id']
                                            sql = f"SELECT name FROM user WHERE id = {user_id}"
                                            name = kyzs_sql.mysql_exec(sql)[0]['name']
                                            
                                            if result:
                                                source['title'] = result[0]['text_title'] + f"（{name}）"               
                                                print(f"更新source标题成功: id={source.get('id')}, title={source['title']}")

                                        except Exception as e:
                                            print(f"更新source标题时出错: {str(e)}")
                            else:
                                print(f"sources不存在或不是列表类型，当前data_json内容: {data_json}")
                    
                        formatted_chunk = f"data: {json.dumps(data_json)}\n\n".encode('utf-8')
                        yield formatted_chunk
                    except json.JSONDecodeError:
                        yield chunk
        
        return generate()
    except requests.RequestException as e:
        def error_generate(exception):
            error_msg = {
                "uuid": str(uuid.uuid4()),
                "type": "error",
                "error": True,
                "message": f"请求出错: {str(exception)}",
                "thread_id": thread_id
            }
            error_chunk = f"data: {json.dumps(error_msg)}\n\n".encode('utf-8')
            yield error_chunk
        
        return error_generate(e)

def get_all_anything_db_api(user_id: int):
    """
    获取所有anything_db中的数据
    """
    sql = f"""
    WITH RECURSIVE folder_tree AS (
        SELECT 
            id,
            folder_name,
            parent_id,
            folder_name AS full_path
        FROM knowledge_folder
        WHERE parent_id IS NULL

        UNION ALL

    SELECT 
        f.id,
        f.folder_name,
        f.parent_id,
        CONCAT(t.full_path, '/', f.folder_name) AS full_path
    FROM knowledge_folder f
    INNER JOIN folder_tree t ON f.parent_id = t.id
        )
        SELECT 
            a.id,
            a.text_title,
            a.publish_date,
            ft.full_path AS folder_path,
            ft.full_path AS full_full_path
        FROM anything_db a
        LEFT JOIN folder_tree ft ON a.folder_id = ft.id
        WHERE a.user_id = {user_id};
        """

    result = kyzs_sql.mysql_exec(sql)
    return result

def delete_anything_db_api(id: int):
    """
    删除所有anything_db中的数据
    """
    sql = f"SELECT text_location FROM anything_db WHERE id = {id}"
    result = kyzs_sql.mysql_exec(sql)
    text_location = result[0]['text_location']

    def delete_text_from_anythingllm(text_location: str):
        llm_ip = settings.anythingllm_base_url
        document_url = llm_ip + f"/api/v1/workspace/{settings.anythingllm_workspace}/update-embeddings"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {settings.anythingllm_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
        "adds": [],
        "deletes": [text_location]
        }
        
        response = requests.post(document_url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        print(f"成功将文档内容从anythingLLM知识库删除，文档位置: {text_location}")
        return result
    
    delete_text_from_anythingllm(text_location)
    
    sql = f"DELETE FROM anything_db WHERE id = {id}"
    kyzs_sql.mysql_exec(sql)
    return 1


def delete_anything_knowledge_by_knowledgeId_api(id:int):
    sql = f"""
    SELECT * FROM anything_db WHERE knowledge_id = {id}
    """
    try:
        anything_id = int(kyzs_sql.mysql_exec(sql)[0]['id'])
    except:
        return {"code": 400, "msg": "anything知识库中没有这个知识", "data": None}

    text_location = kyzs_sql.mysql_exec(sql)[0]['text_location']
    
    sql = f"DELETE FROM anything_db WHERE id = {anything_id}"
    kyzs_sql.mysql_exec(sql)
    
    llm_ip = settings.anythingllm_base_url
    document_url = llm_ip + f"/api/v1/workspace/{settings.anythingllm_workspace}/update-embeddings"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {settings.anythingllm_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
    "adds": [],
    "deletes": [text_location]
    }
    
    response = requests.post(document_url, headers=headers, json=payload)
    response.raise_for_status()
    
    result = response.json()
    print(f"成功将文档内容从anythingLLM知识库删除，文档位置: {text_location}")
    return result


def all_text_to_db(user_id: int,knowledge_id: int,folder_id: int):
    """
    将知识库文本写入到大模型知识库
    """
    sql = f"""
    SELECT * FROM knowledgebase WHERE id = {knowledge_id}
    """
    result = kyzs_sql.mysql_exec(sql)
    if result:
        text = result[0]['content']
        title = result[0]['title']
        sql=f"SELECT * FROM anything_db WHERE text_title = '{title}'"
        if kyzs_sql.mysql_exec(sql):
            return {"code": 400, "msg": "公共知识库中已存在相同标题，不执行插入操作", "data": None}

        def write_text_to_anythingllm(text_title: str,text: str):
            try:
                llm_ip = settings.anythingllm_base_url
                document_url = llm_ip + f"/api/v1/document/raw-text"

                headers = {
                    "accept": "application/json",
                    "Authorization": f"Bearer {settings.anythingllm_api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "textContent": text,
                    "metadata": {
                        "title": text_title,
                        "KeyOne": "0",
                        "KeyTwo": "0",
                        "etc": "etc"
                    }
                }
                
                response = requests.post(document_url, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                print(f"成功将知识库内容写入到大模型知识库")
                
                if result.get('success') and result.get('documents') and len(result['documents']) > 0:
                    document = result['documents'][0]
                    doc_id = document.get('id')
                    location = document.get('location')
                    doc_title = document.get('title')
                    
                    return_result = {
                        'id': doc_id,
                        'location': location,
                        'title': doc_title
                    }
                    
                    print(f"提取的文档信息: {return_result}")
                    return return_result
                else:
                    print("API返回成功但未包含有效的文档信息")
                    return None
                
            except requests.RequestException as e:
                print(f"将知识库内容写入到大模型知识库时出错: {str(e)}")
            except Exception as e:
                print(f"写入大模型知识库时发生未知错误: {str(e)}")
        
        document_info = write_text_to_anythingllm(title,text)
        
        if document_info:
            try:
                insert_sql = f"""
                INSERT INTO anything_db 
                (user_id,knowledge_id,folder_id, text_id, text_title, text_content,text_location) 
                VALUES ({user_id}, {knowledge_id},{folder_id}, '{document_info['id']}', '{title}', '{text}', '{document_info['location']}')
                """
                kyzs_sql.mysql_exec(insert_sql)
                print(f"成功将文档映射关系记录到数据库，用户ID: {user_id}, 知识库ID: {knowledge_id},文件夹ID:{folder_id}")
            except Exception as e:
                print(f"记录文档映射关系到数据库时出错: {str(e)}")
        else:
            print(f"未获取到有效的文档信息，无法记录映射关系")

        def embed_document_to_anythingllm(location: str):
            llm_ip = settings.anythingllm_base_url
            document_url = llm_ip + f"/api/v1/workspace/{settings.anythingllm_workspace}/update-embeddings"
            headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {settings.anythingllm_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
            "adds": [location],
            "deletes": []
            }
            
            response = requests.post(document_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            print(f"成功将文档内容嵌入到anythingLLM知识库，文档位置: {location}")
            return result

        embedding_data = embed_document_to_anythingllm(document_info['location'])

        publish_date = embedding_data.get('workspace')['documents'][-1]['metadata']
        publish_date = json.loads(publish_date).get('published', '')
        print(f"成功提取published日期: {publish_date}")

        sql = f"""
        UPDATE anything_db 
        SET publish_date = '{publish_date}' 
        WHERE text_id = '{document_info['id']}'
        """
        kyzs_sql.mysql_exec(sql)
        print(f"成功将published日期更新到数据库，用户ID: {user_id}, 知识库ID: {knowledge_id}, 文档ID: {document_info['id']}")
        
        return True
    else:
        print(f"用户{user_id}的知识库{knowledge_id}不存在")


def get_public_anything_db_api():
    sql = f"""
    WITH RECURSIVE folder_tree AS (
        SELECT 
            id,
            folder_name,
            parent_id,
            folder_name AS full_path
        FROM knowledge_folder
        WHERE parent_id IS NULL

        UNION ALL

    SELECT 
        f.id,
        f.folder_name,
        f.parent_id,
        CONCAT(t.full_path, '/', f.folder_name) AS full_path
    FROM knowledge_folder f
    INNER JOIN folder_tree t ON f.parent_id = t.id
        )
        SELECT 
            a.id,
            a.text_title,
            a.publish_date,
            ft.full_path AS folder_path
        FROM anything_db a
        LEFT JOIN folder_tree ft ON a.folder_id = ft.id
        """
    result = kyzs_sql.mysql_exec(sql)
    return result


def get_all_folders_api():
    sql = """
    WITH RECURSIVE folder_tree AS (
        SELECT id, folder_name, parent_id, folder_name AS full_path, 1 AS level
        FROM knowledge_folder
        WHERE parent_id IS NULL
        UNION ALL
        SELECT f.id, f.folder_name, f.parent_id,
               CONCAT(t.full_path, '/', f.folder_name), t.level + 1
        FROM knowledge_folder f
        INNER JOIN folder_tree t ON f.parent_id = t.id
    )
    SELECT id, folder_name, parent_id, full_path, level FROM folder_tree ORDER BY full_path;
    """
    result = kyzs_sql.mysql_exec(sql)
    return [dict(r) for r in result]


def get_anythingdb_by_id_api(id: int):
    sql = f"SELECT * FROM anything_db WHERE id = {id}"
    result = kyzs_sql.mysql_exec(sql)
    if result:
        user_id = result[0]['user_id']
        sql = f"SELECT name FROM user WHERE id = {user_id}"
        username_result = kyzs_sql.mysql_exec(sql)
        if username_result:
            username = username_result[0]['name']
        else:
            username = None
        result[0]['username'] = username
        return dict(result[0])
    else:
        return None

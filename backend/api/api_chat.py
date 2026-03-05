import requests
import json
import time
import uuid
from api.sql_role  import kyzs_sql

def stream_chat_handler(message: str):
    """
    处理流式对话请求的内部函数
    :param message: 用户的问题
    :return: 流式响应的生成器
    """
    # 配置LLM服务器信息
    llm_ip = "http://localhost:3001"
    anythingLLMWorkSpace = "kyzs"
    thread_id = "identifier-to-partition-chats-by-external-id"
    anythingLLMKey = "Bearer DKNAE05-JDBMAEN-M2R3BA5-CETY1F2"
    
    # 构建请求URL
    llm_url = llm_ip + f"/api/v1/workspace/{anythingLLMWorkSpace}/stream-chat"
    
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
        # 发送POST请求，启用流式响应
        response = requests.post(llm_url, json=data, headers=headers, stream=True)
        response.raise_for_status()
        
        # 定义生成器函数处理流式响应
        def generate():
            for chunk in response.iter_content(chunk_size=50000):
                if chunk:
                    # 将chunk从bytes转换为字符串
                    chunk_str = chunk.decode('utf-8')
                    try:
                        # 处理响应数据，移除'data: '前缀（如果存在）
                        if chunk_str.startswith('data: '):
                            chunk_str = chunk_str.replace('data: ', '')
                        
                        # 解析JSON数据
                        data_json = json.loads(chunk_str)
                        # print(f"原始chunk: {chunk_str}")

                        # 如果close为True，添加thread_id字段
                        if data_json.get('close', True):

                            # 安全检查sources是否存在并且是列表类型
                            if 'sources' in data_json and isinstance(data_json['sources'], list):
                                for source in data_json['sources']:
                                    # 确保source是字典类型且包含id字段
                                    if isinstance(source, dict) and 'id' in source:
                                        try:
                                            # 获取published字符串
                                            published = source['published']
                                            sql = f"SELECT text_title,user_id FROM anything_db WHERE publish_date = '{published}'"
                                            result = kyzs_sql.mysql_exec(sql)
                                            # print(f"查询结果: {result}")
                                            # 查询用户名
                                            user_id = result[0]['user_id']
                                            sql = f"SELECT name FROM user WHERE id = {user_id}"
                                            name = kyzs_sql.mysql_exec(sql)[0]['name']
                                            # print(f"查询结果: {result}")
                                            
                                            # 如果查询到结果，则更新title
                                            if result:
                                                source['title'] = result[0]['text_title'] + f"（{name}）"               
                                                print(f"更新source标题成功: id={source_id}, title={source['title']}")

                                        except Exception as e:
                                            print(f"更新source标题时出错: {str(e)}")
                                            # 发生异常时不影响整体流程，继续处理其他source
                            else:
                                print(f"sources不存在或不是列表类型，当前data_json内容: {data_json}")
                    
                        # 将修改后的数据重新转换为bytes并添加data:前缀
                        formatted_chunk = f"data: {json.dumps(data_json)}\n\n".encode('utf-8')
                        yield formatted_chunk
                    except json.JSONDecodeError:
                        # 如果不是有效的JSON，直接返回原始chunk
                        yield chunk
        
        # 返回生成器对象
        return generate()
    except requests.RequestException as e:
        # 发生异常时，返回错误信息生成器
        # 将异常对象e作为参数传递给error_generate函数
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
        
        # 调用error_generate函数时传入异常对象e
        return error_generate(e)

def get_all_anything_db_api(user_id: int):
    """
    获取所有anything_db中的数据
    :param user_id: 用户ID
    :return: 所有数据的列表
    """
    sql = f"""
    WITH RECURSIVE folder_tree AS (
        -- 顶层目录
        SELECT 
            id,
            folder_name,
            parent_id,
            folder_name AS full_path
        FROM knowledge_folder
        WHERE parent_id IS NULL

        UNION ALL

    -- 递归拼接路径
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
        WHERE a.user_id = {user_id};   -- 👈 替换成你要查的用户id
        """

    result = kyzs_sql.mysql_exec(sql)
    return result

def delete_anything_db_api(id: int):
    """
    删除所有anything_db中的数据
    :param id: 数据ID
    :return: None
    """
    #从anything中删除
    sql = f"SELECT text_location FROM anything_db WHERE id = {id}"
    result = kyzs_sql.mysql_exec(sql)
    text_location = result[0]['text_location']
    # 将文本写入到大模型知识库文件夹中
    def delete_text_from_anythingllm(text_location: str):
        """
        将文本内容从anythingLLM知识库删除
        使用/api/v1/document/embed接口
        """

        # 构建请求URL
        llm_ip = "http://localhost:3001"
        document_url = llm_ip + f"/api/v1/workspace/kyzs/update-embeddings"
        # 设置请求头
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer DKNAE05-JDBMAEN-M2R3BA5-CETY1F2",
            "Content-Type": "application/json"
        }
        
        # 构建请求体
        payload = {
        "adds": [
            
        ],
        "deletes": [
            text_location
        ]
        }
        
        # 发送POST请求
        response = requests.post(document_url, headers=headers, json=payload)
        response.raise_for_status()
        
        # 处理响应
        result = response.json()
        print(f"成功将文档内容从anythingLLM知识库删除，文档位置: {text_location}")
        return result
    
    # 调用删除函数
    delete_text_from_anythingllm(text_location)
    
    #从数据库中删除
    sql = f"DELETE FROM anything_db WHERE id = {id}"
    kyzs_sql.mysql_exec(sql)
    return 1


#删除指定anything知识库中的内容（以knowledge_id为标识）
def delete_anything_knowledge_by_knowledgeId_api(id:int):

    # 从数据库中查询knowledge_id对应的所有text_location
    sql = f"""
    SELECT * FROM anything_db WHERE knowledge_id = {id}
    """
    try:
        # 如果没有对应的anything_id，则表明anything知识库没有这个知识
        anything_id = int(kyzs_sql.mysql_exec(sql)[0]['id'])
    except:
        return {"code": 400, "msg": "anything知识库中没有这个知识", "data": None}

    text_location = kyzs_sql.mysql_exec(sql)[0]['text_location']
    
    #先在数据库中删除这个id
    sql = f"DELETE FROM anything_db WHERE id = {anything_id}"
    kyzs_sql.mysql_exec(sql)
    

    # 构建请求URL
    llm_ip = "http://localhost:3001"
    document_url = llm_ip + f"/api/v1/workspace/kyzs/update-embeddings"
    # 设置请求头
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer DKNAE05-JDBMAEN-M2R3BA5-CETY1F2",
        "Content-Type": "application/json"
    }
    
    # 构建请求体
    payload = {
    "adds": [
        
    ],
    "deletes": [
        text_location
    ]
    }
    
    # 发送POST请求
    response = requests.post(document_url, headers=headers, json=payload)
    response.raise_for_status()
    
    # 处理响应
    result = response.json()
    print(f"成功将文档内容从anythingLLM知识库删除，文档位置: {text_location}")
    return result



def all_text_to_db(user_id: int,knowledge_id: int,folder_id: int):
    """
    将知识库文本写入到大模型知识库
    :param user_id: 用户ID
    :param knowledge_id: 知识库ID
    :return: None
    """
    # 从数据库中查询知识库文本
    sql = f"""
    SELECT * FROM knowledgebase WHERE id = {knowledge_id}
    """
    result = kyzs_sql.mysql_exec(sql)
    if result:
        text = result[0]['content']
        title = result[0]['title']
        # 先判断这个标题是否在anything知识库中存在了，如果存在则不执行插入操作
        sql=f"SELECT * FROM anything_db WHERE text_title = '{title}'"
        if kyzs_sql.mysql_exec(sql):
            return {"code": 400, "msg": "公共知识库中已存在相同标题，不执行插入操作", "data": None}

        # 将文本写入到大模型知识库文件夹中
        def write_text_to_anythingllm(text_title: str,text: str):
            """
            将文本内容写入到anythingLLM知识库
            使用/api/v1/document/raw-text接口
            """
            try:
                # 构建请求URL
                llm_ip = "http://localhost:3001"
                document_url = llm_ip + f"/api/v1/document/raw-text"
                
                # 设置请求头
                headers = {
                    "accept": "application/json",
                    "Authorization": "Bearer DKNAE05-JDBMAEN-M2R3BA5-CETY1F2",
                    "Content-Type": "application/json"
                }
                
                # 构建请求体
                payload = {
                    "textContent": text,
                    "metadata": {
                        "title": text_title,
                        "KeyOne": "0",
                        "KeyTwo": "0",
                        "etc": "etc"
                    }
                }
                
                # 发送POST请求
                response = requests.post(document_url, headers=headers, json=payload)
                response.raise_for_status()
                
                # 处理响应
                result = response.json()
                print(f"成功将知识库内容写入到大模型知识库")
                
                # 提取需要的字段
                if result.get('success') and result.get('documents') and len(result['documents']) > 0:
                    document = result['documents'][0]
                    doc_id = document.get('id')
                    location = document.get('location')
                    doc_title = document.get('title')
                    
                    # 构建返回结果
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
        
        # 调用函数执行写入操作并获取返回值
        document_info = write_text_to_anythingllm(title,text)
        
        #将此记录到数据库中
        if document_info:
            try:
                # 插入记录到数据库
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


        #将内容嵌入到知识库中
        def embed_document_to_anythingllm(location: str):
            """
            将文本内容嵌入到anythingLLM知识库
            使用/api/v1/document/embed接口
            """

            # 构建请求URL
            llm_ip = "http://localhost:3001"
            document_url = llm_ip + f"/api/v1/workspace/kyzs/update-embeddings"
            # 设置请求头
            headers = {
                "accept": "application/json",
                "Authorization": "Bearer DKNAE05-JDBMAEN-M2R3BA5-CETY1F2",
                "Content-Type": "application/json"
            }
            
            # 构建请求体
            payload = {
            "adds": [
                location
            ],
            "deletes": [

            ]
            }
            
            # 发送POST请求
            response = requests.post(document_url, headers=headers, json=payload)
            response.raise_for_status()
            
            # 处理响应
            result = response.json()
            print(f"成功将文档内容嵌入到anythingLLM知识库，文档位置: {location}")
            return result

        # 调用函数执行嵌入操作
        embedding_data = embed_document_to_anythingllm(document_info['location'])

        #从embed接口返回的数据中拿到publisheddate
        publish_date = embedding_data.get('workspace')['documents'][-1]['metadata']
        publish_date = json.loads(publish_date).get('published', '')
        print(f"成功提取published日期: {publish_date}")

        #将metadata中的published日期更新到数据库对应表中
        sql = f"""
        UPDATE anything_db 
        SET publish_date = '{publish_date}' 
        WHERE text_id = '{document_info['id']}'
        """
        kyzs_sql.mysql_exec(sql)
        print(f"成功将published日期更新到数据库，用户ID: {user_id}, 知识库ID: {knowledge_id}, 文档ID: {document_info['id']}")
        

        # 返回处理结果和文档信息
        return True
    else:
        print(f"用户{user_id}的知识库{knowledge_id}不存在")




def get_public_anything_db_api():
    """
    获取公共知识库下所有数据
    :return: 所有公共数据的列表
    """
    sql = f"""
    WITH RECURSIVE folder_tree AS (
        -- 顶层目录
        SELECT 
            id,
            folder_name,
            parent_id,
            folder_name AS full_path
        FROM knowledge_folder
        WHERE parent_id IS NULL

        UNION ALL

    -- 递归拼接路径
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
    """
    根据ID获取anything_db表中的数据
    :param id: 数据ID
    :return: 对应数据的字典
    """
    sql = f"SELECT * FROM anything_db WHERE id = {id}"
    result = kyzs_sql.mysql_exec(sql)
    if result:
        # 查询user_id对应username
        user_id = result[0]['user_id']
        sql = f"SELECT name FROM user WHERE id = {user_id}"
        username_result = kyzs_sql.mysql_exec(sql)
        if username_result:
            username = username_result[0]['name']
        else:
            username = None
        # 将username添加到结果字典中
        result[0]['username'] = username

        


        return dict(result[0])
    else:
        return None
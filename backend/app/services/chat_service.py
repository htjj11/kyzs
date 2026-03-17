import requests
import json
import uuid
from app.core.database import db as kyzs_sql
from app.config import settings


def stream_chat_handler(message: str):
    """
    向 AnythingLLM 发起流式对话请求，返回 SSE 数据生成器。

    AnythingLLM 的流式响应格式为：
        data: {"id":"...","type":"textResponseChunk","textResponse":"...","close":false}
        ...
        data: {"close":true,"sources":[...]}

    当 close=true 时说明本轮对话结束，sources 包含引用文档元数据。
    此处在结束帧中查询数据库，将 source 的 published 时间戳映射为可读标题。
    """
    llm_url = settings.anythingllm_base_url + f"/api/v1/workspace/{settings.anythingllm_workspace}/stream-chat"
    headers = {"Authorization": f"Bearer {settings.anythingllm_api_key}"}
    data = {"message": message, "mode": "chat"}

    try:
        response = requests.post(llm_url, json=data, headers=headers, stream=True)
        response.raise_for_status()

        def generate():
            for chunk in response.iter_content(chunk_size=50000):
                if not chunk:
                    continue
                chunk_str = chunk.decode('utf-8')
                try:
                    if chunk_str.startswith('data: '):
                        chunk_str = chunk_str[6:]
                    data_json = json.loads(chunk_str)

                    # 最后一帧：用 publish_date 反查 anything_db 获取原始标题
                    if data_json.get('close', True):
                        sources = data_json.get('sources')
                        if sources is not None and isinstance(sources, list):
                            for source in sources:
                                if not isinstance(source, dict) or 'id' not in source:
                                    continue
                                try:
                                    published = source.get('published')
                                    result = kyzs_sql.mysql_exec(
                                        "SELECT text_title, user_id FROM anything_db WHERE publish_date=%s",
                                        (published,)
                                    )
                                    if result:
                                        name_result = kyzs_sql.mysql_exec(
                                            "SELECT name FROM user WHERE id=%s",
                                            (result[0]['user_id'],)
                                        )
                                        if name_result:
                                            source['title'] = result[0]['text_title'] + f"（{name_result[0]['name']}）"
                                            print(f"更新source标题成功: id={source.get('id')}, title={source['title']}")
                                except Exception as e:
                                    print(f"更新source标题时出错: {e}")
                        else:
                            print(f"sources不存在或不是列表类型，当前data_json内容: {data_json}")

                    yield f"data: {json.dumps(data_json)}\n\n".encode('utf-8')
                except json.JSONDecodeError:
                    yield chunk

        return generate()

    except requests.RequestException as e:
        def error_generate(exception):
            error_msg = {
                "uuid": str(uuid.uuid4()), "type": "error", "error": True,
                "message": f"请求出错: {str(exception)}"
            }
            yield f"data: {json.dumps(error_msg)}\n\n".encode('utf-8')
        return error_generate(e)


def get_all_anything_db_api(user_id: int):
    # WITH RECURSIVE 递归 CTE 拼接文件夹完整路径（例如 "政策与标准/国家政策/法规"）
    sql = """
    WITH RECURSIVE folder_tree AS (
        SELECT id, folder_name, parent_id, folder_name AS full_path
        FROM knowledge_folder WHERE parent_id IS NULL
        UNION ALL
        SELECT f.id, f.folder_name, f.parent_id, CONCAT(t.full_path, '/', f.folder_name)
        FROM knowledge_folder f
        INNER JOIN folder_tree t ON f.parent_id = t.id
    )
    SELECT a.id, a.text_title, a.publish_date,
           ft.full_path AS folder_path, ft.full_path AS full_full_path
    FROM anything_db a
    LEFT JOIN folder_tree ft ON a.folder_id = ft.id
    WHERE a.user_id = %s
    """
    return kyzs_sql.mysql_exec(sql, (user_id,))


def delete_anything_db_api(id: int):
    """
    删除 AnythingLLM 向量库中的文档，并同步删除本地数据库记录。
    必须先从向量库删除（update-embeddings），再删数据库，避免数据不一致。
    """
    result = kyzs_sql.mysql_exec("SELECT text_location FROM anything_db WHERE id=%s", (id,))
    text_location = result[0]['text_location']

    document_url = settings.anythingllm_base_url + f"/api/v1/workspace/{settings.anythingllm_workspace}/update-embeddings"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {settings.anythingllm_api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(document_url, headers=headers, json={"adds": [], "deletes": [text_location]})
    response.raise_for_status()
    print(f"成功将文档内容从anythingLLM知识库删除，文档位置: {text_location}")

    kyzs_sql.mysql_exec("DELETE FROM anything_db WHERE id=%s", (id,))
    return 1


def delete_anything_knowledge_by_knowledgeId_api(id: int):
    """
    通过知识库 knowledge_id 删除对应的 AnythingLLM 向量文档。
    在删除 knowledgebase 记录时联动调用，保持向量库与数据库同步。
    """
    result = kyzs_sql.mysql_exec("SELECT * FROM anything_db WHERE knowledge_id=%s", (id,))
    if not result:
        return {"code": 400, "msg": "anything知识库中没有这个知识", "data": None}

    anything_id = int(result[0]['id'])
    text_location = result[0]['text_location']
    kyzs_sql.mysql_exec("DELETE FROM anything_db WHERE id=%s", (anything_id,))

    document_url = settings.anythingllm_base_url + f"/api/v1/workspace/{settings.anythingllm_workspace}/update-embeddings"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {settings.anythingllm_api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(document_url, headers=headers, json={"adds": [], "deletes": [text_location]})
    response.raise_for_status()
    result = response.json()
    print(f"成功将文档内容从anythingLLM知识库删除，文档位置: {text_location}")
    return result


def all_text_to_db(user_id: int, knowledge_id: int, folder_id: int):
    """
    将 knowledgebase 中的文本上传到 AnythingLLM 并嵌入向量库。

    流程：
        1. 查询 knowledgebase 获取文本内容
        2. POST /api/v1/document/raw-text 上传原始文本，获取 doc_id 和 location
        3. 将映射关系写入 anything_db
        4. POST /api/v1/workspace/{slug}/update-embeddings 触发向量化
        5. 从嵌入响应中提取 published 时间戳，回写到 anything_db（用于后续 source 标题映射）
    """
    result = kyzs_sql.mysql_exec("SELECT * FROM knowledgebase WHERE id=%s", (knowledge_id,))
    if not result:
        print(f"用户{user_id}的知识库{knowledge_id}不存在")
        return None

    text = result[0]['content']
    title = result[0]['title']

    if kyzs_sql.mysql_exec("SELECT id FROM anything_db WHERE text_title=%s", (title,)):
        return {"code": 400, "msg": "公共知识库中已存在相同标题，不执行插入操作", "data": None}

    try:
        document_url = settings.anythingllm_base_url + "/api/v1/document/raw-text"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {settings.anythingllm_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "textContent": text,
            "metadata": {"title": title, "KeyOne": "0", "KeyTwo": "0"}
        }
        response = requests.post(document_url, headers=headers, json=payload)
        response.raise_for_status()
        api_result = response.json()
        print(f"成功将知识库内容写入到大模型知识库")

        if not (api_result.get('success') and api_result.get('documents')):
            print("API返回成功但未包含有效的文档信息")
            return None

        document = api_result['documents'][0]
        doc_id = document.get('id')
        location = document.get('location')
        return_result = {'id': doc_id, 'location': location, 'title': document.get('title')}
        print(f"提取的文档信息: {return_result}")

        kyzs_sql.mysql_exec(
            """INSERT INTO anything_db
               (user_id, knowledge_id, folder_id, text_id, text_title, text_content, text_location)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (user_id, knowledge_id, folder_id, doc_id, title, text, location)
        )
        print(f"成功将文档映射关系记录到数据库，用户ID: {user_id}, 知识库ID: {knowledge_id},文件夹ID:{folder_id}")
    except requests.RequestException as e:
        print(f"将知识库内容写入到大模型知识库时出错: {str(e)}")
        return None
    except Exception as e:
        print(f"写入大模型知识库时发生未知错误: {str(e)}")
        return None

    # 触发向量化嵌入
    embed_url = settings.anythingllm_base_url + f"/api/v1/workspace/{settings.anythingllm_workspace}/update-embeddings"
    embedding_resp = requests.post(embed_url, headers=headers, json={"adds": [location], "deletes": []})
    embedding_resp.raise_for_status()
    embedding_data = embedding_resp.json()
    print(f"成功将文档内容嵌入到anythingLLM知识库，文档位置: {location}")

    try:
        # AnythingLLM 在嵌入后会生成 published 字段作为文档唯一时间戳
        # 将其存入数据库，用于流式对话结束帧中反查文档标题
        publish_date = embedding_data.get('workspace')['documents'][-1]['metadata']
        publish_date = json.loads(publish_date).get('published', '')
        print(f"成功提取published日期: {publish_date}")
        kyzs_sql.mysql_exec(
            "UPDATE anything_db SET publish_date=%s WHERE text_id=%s",
            (publish_date, doc_id)
        )
        print(f"成功将published日期更新到数据库，用户ID: {user_id}, 知识库ID: {knowledge_id}, 文档ID: {doc_id}")
    except Exception as e:
        print(f"更新publish_date时出错: {e}")

    return True


def get_public_anything_db_api():
    # 公共知识库不过滤 user_id，展示所有用户上传的文档
    sql = """
    WITH RECURSIVE folder_tree AS (
        SELECT id, folder_name, parent_id, folder_name AS full_path
        FROM knowledge_folder WHERE parent_id IS NULL
        UNION ALL
        SELECT f.id, f.folder_name, f.parent_id, CONCAT(t.full_path, '/', f.folder_name)
        FROM knowledge_folder f
        INNER JOIN folder_tree t ON f.parent_id = t.id
    )
    SELECT a.id, a.text_title, a.publish_date, ft.full_path AS folder_path
    FROM anything_db a
    LEFT JOIN folder_tree ft ON a.folder_id = ft.id
    """
    return kyzs_sql.mysql_exec(sql)


def get_all_folders_api():
    # level 字段用于前端渲染树形结构的缩进层级
    sql = """
    WITH RECURSIVE folder_tree AS (
        SELECT id, folder_name, parent_id, folder_name AS full_path, 1 AS level
        FROM knowledge_folder WHERE parent_id IS NULL
        UNION ALL
        SELECT f.id, f.folder_name, f.parent_id,
               CONCAT(t.full_path, '/', f.folder_name), t.level + 1
        FROM knowledge_folder f
        INNER JOIN folder_tree t ON f.parent_id = t.id
    )
    SELECT id, folder_name, parent_id, full_path, level FROM folder_tree ORDER BY full_path
    """
    return [dict(r) for r in kyzs_sql.mysql_exec(sql)]


def get_anythingdb_by_id_api(id: int):
    result = kyzs_sql.mysql_exec("SELECT * FROM anything_db WHERE id=%s", (id,))
    if not result:
        return None
    row = dict(result[0])
    name_result = kyzs_sql.mysql_exec("SELECT name FROM user WHERE id=%s", (row['user_id'],))
    row['username'] = name_result[0]['name'] if name_result else None
    return row

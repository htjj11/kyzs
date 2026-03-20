import requests
import json
import datetime
import os
import pypandoc
import base64
import hashlib
import time
import urllib.parse
import xml.etree.ElementTree as ET
from core.sqlLiteExec import sqlite_execute


def get_xunfei_api(keyword: str):
    def xunfei_online_search(question):
        url = "https://spark-api-open.xf-yun.com/v1/chat/completions"
        print(f'方法内：讯飞网络知识检索关键词：{question}', flush=True)
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_research_information",
                    "description": "获取互联网科研信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "信息标题"},
                            "content": {"type": "string", "description": "信息内容，约1000字，倾向于真实案例和数据"},
                            "source": {"type": "string", "description": "信息来源"},
                            "date": {"type": "string", "description": "信息日期，格式为YYYY-MM-DD"},
                            "author": {"type": "string", "description": "信息作者"}
                        },
                        "required": ["title", "content", "source", "date", "author"]
                    }
                }
            },
            {
                "type": "web_search",
                "web_search": {"enable": True, "show_ref_label": True, "search_mode": "deep"}
            }
        ]
        data = {
            "model": "4.0Ultra",
            "user": "default_user",
            "messages": [
                {"role": "system", "content": "你是知识渊博的助理，能够获取互联网科研信息"},
                {"role": "user", "content": question}
            ],
            "temperature": 1,
            "top_k": 6,
            "stream": False,
            "max_tokens": 5000,
            "tools": tools,
            "tool_choice": {"type": "function", "function": {"name": "get_research_information"}},
        }
        header = {"Authorization": f"Bearer fXMOutpFGqmwUoTTSpHz:OTsqdwPkqNmvlKJouKSU"}
        print(f'准备执行请求：{url}，请求头：{header}，请求数据：{data}', flush=True)
        try:
            response = requests.post(url, headers=header, json=data)
            print(f'请求已发送，等待响应...', flush=True)
            return response.json()
        except Exception as e:
            print(f'发送请求时出错：{e}', flush=True)
            return None

    return xunfei_online_search(keyword)


def siliconflow_deepseek_answer(question):
    """
    调用 SiliconFlow 托管的 DeepSeek-V3 模型进行问答。
    stream=False 为同步调用，适合需要完整响应的场景（翻译、综述生成等）。
    流式对话场景请使用 AnythingLLM 的 stream-chat 接口。
    """
    url = "https://api.siliconflow.cn/v1/chat/completions"
    payload = {
        "model": "Pro/deepseek-ai/DeepSeek-V3",
        "messages": [{"role": "user", "content": str(question)}],
        "stream": False,
        "max_tokens": 8192,
        "stop": ["null"],
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"},
        "tools": [
            {
                "type": "function",
                "function": {
                    "description": "<string>",
                    "name": "<string>",
                    "parameters": {},
                    "strict": False
                }
            }
        ]
    }
    headers = {
        "Authorization": f"Bearer sk-wmsgbfgsvjxjmyopswmaqfxnwtgmvtwqgsigehxmgwoihgeg",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    content = response.json()['choices'][0]['message']['content']
    print(f"deepseek返回: {content}")
    return content


def add_article_to_knowledge(article_data: dict, label_id: int, user_id: int):
    title = str(article_data.get('title_zh', article_data['title'])).replace("\n", "")
    abstract = article_data.get('abstract_zh', article_data.get('abstract', ''))
    keywords = article_data.get('keywords_zh', article_data['keywords'])
    content = f"文献信息如下:    标题：{title}    摘要：{abstract}    关键词：{keywords}    "
    mark_info = article_data.get('doi')
    sqlite_execute(
        "INSERT INTO `knowledgebase` (title, content, label_id, user_id, type_id, mark_info) VALUES (?,?,?,?,?,?)",
        (title, content, label_id, user_id, 1, mark_info)
    )
    return {'code': 200, 'msg': 'success', 'data': None}


def add_patent_to_knowledge(patent_data: dict, label_id: int, user_id: int):
    id = patent_data.get('id')
    title = str(patent_data.get('title'))
    abstract = str(patent_data.get('abstract'))
    country = str(patent_data.get('country'))
    app_num = str(patent_data.get('app_num'))
    app_date = datetime.datetime.strptime(str(patent_data.get('app_date')), '%Y-%m-%dT%H:%M:%S')
    pub_num = str(patent_data.get('pub_num'))
    pub_date = datetime.datetime.strptime(str(patent_data.get('pub_date')), '%Y-%m-%dT%H:%M:%S')
    pub_kind = str(patent_data.get('pub_kind'))
    applicant = str(patent_data.get('applicant'))
    content = (
        f"专利摘要：{abstract}\n专利国家：{country}\n专利申请号：{app_num}\n"
        f"专利申请日期：{app_date}\n专利公开号：{pub_num}\n专利公开日期：{pub_date}\n"
        f"专利公开类型：{pub_kind}\n专利申请人：{applicant}\n"
    )
    sqlite_execute(
        "INSERT INTO knowledgebase (title, content, label_id, user_id, type_id, mark_info) VALUES (?,?,?,?,?,?)",
        (title, content, label_id, user_id, 2, id)
    )
    return {'code': 200, 'msg': 'success', 'data': None}


def add_online_infomation_to_knowledge(online_infomation: dict, label_id: int, user_id: int):
    content = (
        f"日期：{online_infomation['date']}\n标题：{online_infomation['title']}\n"
        f"内容：{online_infomation['content']}\n来源：{online_infomation['source']}\n"
    )
    sql = "INSERT INTO knowledgebase (title, content, label_id, user_id, type_id, mark_info) VALUES (%s,%s,%s,%s,3,'网络信息收藏')"
    print("\033[31m" + "收藏互联网信息：" + sql + "\033[0m")
    kyzs_sql.mysql_exec(sql, (online_infomation['title'], content, label_id, user_id))
    return {'code': 200, 'msg': 'success', 'data': None}


def add_mycontent_to_knowledge(content: str, title: str, label_id: int, user_id: int):
    sql = "INSERT INTO knowledgebase (title, content, label_id, user_id, type_id, mark_info) VALUES (%s,%s,%s,%s,4,'用户自定义上传信息')"
    print("\033[31m" + "添加用户自定义内容：" + sql + "\033[0m")
    kyzs_sql.mysql_exec(sql, (title, content, label_id, user_id))
    return {'code': 200, 'msg': 'success', 'data': None}


def add_mycontent_file_to_knowledge(file_base64_string: str, file_extension: str, title: str, label_id: int, user_id: int):
    """
    解析上传文件列表（PDF/DOCX/TXT/PPTX）并将文本内容存入知识库。
    文件以 base64 字符串传输，保存到file_data目录中，并重命名为纯数字（以毫秒级别时间戳命名）。
    同一用户下文件标题唯一，重复上传会返回 400。
    """
    print(f'传入base64{file_base64_string[:100]}')
    existing = sqlite_execute(
        "SELECT id FROM knowledgebase WHERE title=? AND user_id=?", (title, user_id)
    )
    if existing:
        return {"code": 400, "msg": "数据库当前用户中已存在相同文件名，不执行插入操作", "data": None}

    os.makedirs("file_data", exist_ok=True)
    file_ext = str(file_extension).replace(".", "")
    new_filename = f"{int(time.time() * 1000)}.{file_ext}"
    file_path = os.path.join("file_data", new_filename)

    try:
        binary = base64.b64decode(file_base64_string)
        with open(file_path, "wb") as f:
            f.write(binary)
    except Exception:
        return {"code": 500, "msg": "Invalid Base64 string", "data": None}

    def text_extraction(path, file_type):
        def pdf_handler(p):
            from pypdf import PdfReader
            reader = PdfReader(p)
            return "".join(page.extract_text() or "" for page in reader.pages)

        def docx_handler(p):
            from docx import Document
            document = Document(p)
            return "".join(p_obj.text for p_obj in document.paragraphs)

        def txt_handler(p):
            with open(p, "rb") as f:
                return f.read().decode('utf-8')

        def ppt_handler(p):
            from pptx import Presentation
            prs = Presentation(p)
            return "".join(
                shape.text + "\n"
                for slide in prs.slides
                for shape in slide.shapes
                if hasattr(shape, "text")
            )

        handlers = {"txt": txt_handler, "docx": docx_handler, "pdf": pdf_handler, "pptx": ppt_handler}
        handler = handlers.get(file_type)
        if handler:
            return handler(path)
        return ""

    content_string = text_extraction(file_path, file_ext)
    # 删除\n，部分pdf会包含\n
    content_string = content_string.replace("\n", "")
    
    mark_info_dict = {
        "filename": new_filename,
        "original_filename": f"{title}.{file_ext}"
    }
    mark_info_str = json.dumps(mark_info_dict, ensure_ascii=False)
    
    sqlite_execute(
        "INSERT INTO knowledgebase (title, content, label_id, user_id, type_id, mark_info) VALUES (?,?,?,?,5,?)",
        (title, content_string, label_id, user_id, mark_info_str)
    )
    return {'code': 200, 'msg': 'success', 'data': None}


def modify_summary_api(review_id: int, start_position: int, end_position: int, replaced_text: str):
    result = kyzs_sql.mysql_exec(
        "SELECT review_body FROM review_records WHERE id=%s", (review_id,)
    )
    original_text = result[0]['review_body']
    new_text = original_text[:start_position] + replaced_text + original_text[end_position:]
    kyzs_sql.mysql_exec(
        "UPDATE review_records SET review_body=%s WHERE id=%s", (new_text, review_id)
    )
    return 1


def modify_review_new_api(review_id: int, review_body: str):
    kyzs_sql.mysql_exec(
        "UPDATE review_records SET review_body=%s WHERE id=%s", (review_body, review_id)
    )
    return 1


def delete_summary(id: int):
    kyzs_sql.mysql_exec("DELETE FROM review_records WHERE id=%s", (id,))
    return 1


def generate_word_api(id: int):
    """
    将综述正文（Markdown 格式）转换为 Word 文档，以 base64 返回。
    依赖系统安装的 pandoc，需提前执行 brew install pandoc（macOS）或对应安装命令。
    """
    sql = "SELECT * FROM review_records WHERE id=%s"
    print("\033[31m" + "获取综述内容用于生成word：" + sql + "\033[0m")
    data = kyzs_sql.mysql_exec(sql, (id,))
    if not data:
        return {'code': 400, 'msg': '未找到该综述', 'data': None}

    md_text = data[0]['review_body']
    md_text = md_text.replace('\\n', '\n').replace('```markdown', '').replace('```', '')

    with open('temp.md', 'w', encoding='utf-8') as f:
        f.write(md_text)

    output_path = "temp_output_word.docx"
    pypandoc.convert_file('temp.md', to='docx', outputfile=output_path)
    with open(output_path, 'rb') as f:
        word_binary = f.read()

    os.remove('temp.md')
    os.remove(output_path)

    word_64 = base64.b64encode(word_binary).decode('utf-8')
    print('生成word文档成功')
    return {'code': 200, 'msg': 'success', 'data': word_64}


def generate_fuwenben_word_api(id: int):
    sql = "SELECT * FROM review_records WHERE id=%s"
    print("\033[31m" + "获取综述内容用于生成word：" + sql + "\033[0m")
    data = kyzs_sql.mysql_exec(sql, (id,))
    if not data:
        return {'code': 400, 'msg': '未找到该综述', 'data': None}

    html_text = data[0]['review_body']

    from docx import Document
    from bs4 import BeautifulSoup
    from io import BytesIO

    doc = Document()
    soup = BeautifulSoup(html_text, 'html.parser')

    def process_element(element, parent_paragraph=None):
        if element.name is None:
            if parent_paragraph:
                parent_paragraph.add_run(str(element))
            return
        if element.name in ['p', 'div', 'br']:
            new_p = doc.add_paragraph()
            for child in element.children:
                process_element(child, new_p)
        elif element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            doc.add_heading(element.get_text(strip=False), level=int(element.name[1]))
        elif element.name in ['strong', 'b']:
            if parent_paragraph:
                run = parent_paragraph.add_run(element.get_text())
                run.bold = True
        elif element.name in ['em', 'i']:
            if parent_paragraph:
                run = parent_paragraph.add_run(element.get_text())
                run.italic = True
        else:
            for child in element.children:
                process_element(child, parent_paragraph)

    for child in soup.children:
        process_element(child)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    word_b64 = base64.b64encode(buffer.read()).decode('utf-8')
    return {'code': 200, 'msg': 'success', 'data': word_b64}

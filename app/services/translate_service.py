from app.core.database import db as kyzs_sql
import base64
from pdf2docx import parse
from docx import Document
from docx2pdf import convert
import json
import random
import re
import concurrent.futures

from app.services.literature_service import siliconflow_deepseek_answer


def translate_text_api(raw_text:str,translate_type:str,field_id:int):
    """
    翻译单个字符串的函数
    :param raw_text: 原始文本
    :param translate_type: 翻译类型,en2zh:英文到中文,zh2en:中文到英文
    :param field_id: 领域id
    :return: 翻译后的文本
    """
    print('用户请求翻译:',raw_text[:40],'...',)
    word_ts_type = {
        'en2zh':'en',
        'zh2en':'en',
    }
    ts_type = word_ts_type[translate_type]
    sql = f"select * from translate_words where ts_type='{ts_type}' and field_id={field_id}"
    words_dict = kyzs_sql.mysql_exec(sql)
    new_words_dict = []

    word_index =  {'en2zh':'content1','zh2en':'content2'}
    lower_paragraph = raw_text.lower()
    for i in words_dict:
        lower_word = i[word_index[translate_type]].lower()
        pattern = r'\b' + re.escape(lower_word) + r'\b'
        if re.search(pattern, lower_paragraph):
            new_words_dict.append(i)
            
    print('知识库命中字典个数:',new_words_dict.__len__())
    prompt = '以下是文中存在的词汇对照组，可用于参考：\n'
    for i in new_words_dict:
        prompt += f"{i[word_index[translate_type]]}：{i['content2']}，解释：{i['content3']}  "
    prompt += f"\n请翻译以下文本（单词）为中文：【{raw_text}】，输出格式为json：origin_text为原文,translate_text为译文，不要有任何其他信息、提问，只返回json即可"

    while 1:
        res = siliconflow_deepseek_answer(prompt)
        try:
            res = res.replace('```json','').replace('```','')
            res_json = json.loads(res)
            translate_text = res_json['translate_text']
            print('大模型翻译成功：',translate_text)
            break
        except Exception as e:
            print('大模型返回的结果格式错误:错误信息:',e)
            continue

    return {'translate_result':translate_text,'words_dict':new_words_dict}


def translate_text_list_api(raw_text_list:list,translate_type:str,field_id:int):
    """
    翻译函数（多线程并发）
    """
    translate_results = [None] * len(raw_text_list)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(translate_text_api, text, translate_type, field_id): index for index, text in enumerate(raw_text_list)}
        for future in concurrent.futures.as_completed(futures):
            index = futures[future]
            try:
                result = future.result()
                translate_results[index] = result['translate_result']
            except Exception as e:
                print(f"翻译出错: {e}")
                translate_results[index] = "该段翻译失败"
    return translate_results

def create_new_translate_doc_mission(base64_pdf_string,topic,user_id):
    '''
    创建新的翻译任务，先创建翻译任务，然后执行翻译方法，翻译后保存到数据库中
    '''
    sql = f"insert into translate_doc (name,status,raw_base64,user_id) values ('{topic}',0,'{base64_pdf_string}','{user_id}')"
    kyzs_sql.mysql_exec(sql)
    sql = "select id from translate_doc order by id desc limit 1"
    mission_id = kyzs_sql.mysql_exec(sql)[0]['id']
    output_docx_base64,output_pdf_base64 = translate_pdf(base64_pdf_string)
    import time
    file_name = time.strftime("%Y%m%d%H%M%S", time.localtime())
    with open(f'./file/{file_name}.pdf', 'wb') as f:
        f.write(base64.b64decode(output_pdf_base64))
    with open(f'./file/{file_name}.docx', 'wb') as f:
        f.write(base64.b64decode(output_docx_base64))
    sql = f"update translate_doc set status=1,output_pdf_base64='./file/{file_name}.pdf',output_docx_base64='./file/{file_name}.docx' where id={mission_id}"
    kyzs_sql.mysql_exec(sql)
    print('翻译任务id成功:',mission_id)

    return 'ok'


def translate_pdf(base64_pdf_string):
    import base64
    from pdf2docx import parse
    from docx import Document
    from docx2pdf import convert
    import os
    try:
        pdf_binary = base64.b64decode(base64_pdf_string)
    except:
        return "Invalid Base64 string"
    
    with open("temp.pdf", "wb") as f:
        f.write(pdf_binary)
    try:
        parse("temp.pdf","input.docx")
    except Exception as e :
        print(f"{e}")

    document = Document('input.docx')
    list_paragraphs = [] 
    for paragraph in document.paragraphs:
        if any("pic:pic" in run.element.xml for run in paragraph.runs):
            continue
        init = 1
        for run in paragraph.runs:
            if init:
                init = 0
                list_paragraphs.append(paragraph.text)
            else:
                run.text = ""
    translated_list_paragraphs = translate_text_list_api(list_paragraphs,'en2zh',1)
    p_index = 0
    for paragraph in document.paragraphs:
        if any("pic:pic" in run.element.xml for run in paragraph.runs):
            continue
        init = 1
        for run in paragraph.runs:
            if init:
                init = 0
                run.text = translated_list_paragraphs[p_index]
                p_index += 1
            else:
                run.text = ""
    document.save('output.docx')
    try:
        convert("output.docx", "output.pdf")
    except:
        pass
    with open("output.docx", "rb") as f:
        output_binary_docx = f.read()
    base64_output_string_docx = base64.b64encode(output_binary_docx).decode('utf-8')
    
    with open("output.pdf", "rb") as f:
        output_binary_pdf = f.read()
    base64_output_string_pdf = base64.b64encode(output_binary_pdf).decode('utf-8')
    
    os.remove("temp.pdf")
    os.remove("input.docx")
    
    return [base64_output_string_docx, base64_output_string_pdf]

def get_all_translate_doc_list_api(user_id):
    sql = f"select id,name,status from translate_doc where user_id={user_id}"
    res = kyzs_sql.mysql_exec(sql)
    return {'translate_doc_list':res}

def get_translate_doc_detail_api(doc_id):
    sql = f"select output_pdf_base64,output_docx_base64 from translate_doc where id={doc_id}"
    res = kyzs_sql.mysql_exec(sql)[0]

    with open(res['output_pdf_base64'], 'rb') as f:
        output_binary_pdf = f.read()
    base64_output_string_pdf = base64.b64encode(output_binary_pdf).decode('utf-8')

    with open(res['output_docx_base64'], 'rb') as f:
        output_binary_docx = f.read()
    base64_output_string_docx = base64.b64encode(output_binary_docx).decode('utf-8')

    res['output_pdf_base64'] = base64_output_string_pdf
    res['output_docx_base64'] = base64_output_string_docx
    return {'translate_doc_detail':res}

def del_translate_doc_api(doc_id):
    sql = f"select output_pdf_base64,output_docx_base64 from translate_doc where id={doc_id}"
    res = kyzs_sql.mysql_exec(sql)[0]
    import os
    os.remove(res['output_pdf_base64'])
    os.remove(res['output_docx_base64'])

    sql = f"delete from translate_doc where id={doc_id}"
    kyzs_sql.mysql_exec(sql)

    return 'ok'


def get_translate_word_by_content_api(content1: str):
    escaped_keyword = content1.replace("'", "''")
    sql = f"SELECT * FROM translate_words WHERE content1 LIKE '%{escaped_keyword}%' OR content2 LIKE '%{escaped_keyword}%' limit 50"
    res = kyzs_sql.mysql_exec(sql)
    if res:
        return {'code': 200, 'msg': 'success', 'data': res}
    else:
        return {'code': 404, 'msg': '词汇不存在', 'data': None}

def add_translate_word_api(ts_type: str, field_id: int, content1: str, content2: str, content3: str, from_source: str):
    sql = f"""
    INSERT INTO translate_words (ts_type, field_id, content1, content2, content3, `from`) 
    VALUES ('{ts_type}', {field_id}, '{content1}', '{content2}', '{content3}', '{from_source}')
    """
    try:
        kyzs_sql.mysql_exec(sql)
        sql = "SELECT id FROM translate_words ORDER BY id DESC LIMIT 1"
        new_id = kyzs_sql.mysql_exec(sql)[0]['id']
        return {'code': 200, 'msg': 'success', 'data': {'id': new_id}}
    except Exception as e:
        return {'code': 500, 'msg': f'添加失败: {str(e)}', 'data': None}

def update_translate_word_api(word_id: int, ts_type: str = None, field_id: int = None, 
                             content1: str = None, content2: str = None, content3: str = None, from_source: str = None):
    update_fields = []
    if ts_type is not None:
        update_fields.append(f"ts_type = '{ts_type}'")
    if field_id is not None:
        update_fields.append(f"field_id = {field_id}")
    if content1 is not None:
        update_fields.append(f"content1 = '{content1}'")
    if content2 is not None:
        update_fields.append(f"content2 = '{content2}'")
    if content3 is not None:
        update_fields.append(f"content3 = '{content3}'")
    if from_source is not None:
        update_fields.append(f"`from` = '{from_source}'")
    
    if not update_fields:
        return {'code': 400, 'msg': '没有提供要更新的字段', 'data': None}
    
    sql = f"UPDATE translate_words SET {', '.join(update_fields)} WHERE id = {word_id}"
    try:
        kyzs_sql.mysql_exec(sql)
        return {'code': 200, 'msg': 'success', 'data': None}
    except Exception as e:
        return {'code': 500, 'msg': f'更新失败: {str(e)}', 'data': None}

def delete_translate_word_api(word_id: int):
    sql = f"DELETE FROM translate_words WHERE id = {word_id}"
    try:
        kyzs_sql.mysql_exec(sql)
        return {'code': 200, 'msg': 'success', 'data': None}
    except Exception as e:
        return {'code': 500, 'msg': f'删除失败: {str(e)}', 'data': None}

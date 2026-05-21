import base64
import tempfile
import os
import re
from docx import Document
from htmldocx import HtmlToDocx

def html_to_word_base64(html_content: str) -> str:
    tmp_files = []  # 记录所有临时文件，最后统一删除

    def replace_base64_images(html: str) -> str:
        """将 base64 图片替换为临时文件路径"""
        def replacer(match):
            ext = match.group(1)   # png / jpeg / gif 等
            data = match.group(2)  # base64 数据
            
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{ext}')
            tmp.write(base64.b64decode(data))
            tmp.close()
            tmp_files.append(tmp.name)
            
            return f'src="{tmp.name}"'
        
        return re.sub(
            r'src="data:image/(\w+);base64,([^"]+)"',
            replacer,
            html
        )

    tmp_docx = tempfile.mktemp(suffix='.docx')
    try:
        html_content = replace_base64_images(html_content)

        doc = Document()
        parser = HtmlToDocx()
        parser.add_html_to_document(html_content, doc)
        doc.save(tmp_docx)

        with open(tmp_docx, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    finally:
        # 删除 docx 临时文件
        if os.path.exists(tmp_docx):
            os.remove(tmp_docx)
        # 删除所有图片临时文件
        for f in tmp_files:
            if os.path.exists(f):
                os.remove(f)
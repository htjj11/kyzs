import json


def extract_json(text: str) -> dict:
    """
    从文本中提取 JSON 字符串并解析为 Python 字典。
    传入样例：
    ```json
    {
    "content": "等待时不阻塞事件循环，可运行其他协程。"
    }
    ```
    :param text: 包含 JSON 字符串的文本
    :return: 解析后的 Python 字典
    """

    # 删除 ```json 和 ``` 
    text = text.replace('```json', '').replace('```', '')
    # 解析为 Python 字典
    data = json.loads(text)
    return data

# import pypandoc

# # 下载并安装 pandoc
# pypandoc.download_pandoc()
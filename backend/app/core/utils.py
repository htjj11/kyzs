import json


def extract_json(text: str) -> dict:
    """
    从 LLM 返回文本中提取 JSON 块并解析为 dict。
    支持 ```json ... ``` 格式的包裹。
    """
    text = text.replace("```json", "").replace("```", "")
    return json.loads(text)

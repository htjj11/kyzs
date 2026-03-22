import requests
#基于讯飞网络知识检索获取信息
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

#基于ai回答问题
def siliconflow_deepseek_answer(question):
    """
    调用 SiliconFlow 托管的 DeepSeek-V3 模型进行问答。
    stream=False 为同步调用，适合需要完整响应的场景（翻译、综述生成等）。
    流式对话场景请使用 AnythingLLM 的 stream-chat 接口。
    """
    url = "https://api.siliconflow.cn/v1/chat/completions"
    payload = {
        "model": "deepseek-ai/DeepSeek-V3.2",
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

import requests
import json



def _normalize_metaso_to_xunfei_shape(result: dict) -> dict:
    """将秘塔 /search/v2 返回的 data 转为与讯飞接口相近的 choices 结构，供前端解析。"""
    text = (result or {}).get("text") or ""
    refs = (result or {}).get("references") or []
    outputs = []
    for r in refs:
        if not isinstance(r, dict):
            continue
        title = r.get("title") or r.get("name") or r.get("snippet") or ""
        url = r.get("url") or r.get("link") or r.get("href") or ""
        outputs.append({"title": str(title), "url": str(url)})
    return {
        "choices": [
            {"message": {"role": "assistant", "content": text}},
            {
                "message": {
                    "role": "tool",
                    "tool_calls": [
                        {
                            "type": "web_search",
                            "web_search": {"outputs": outputs},
                        }
                    ],
                }
            },
        ]
    }


def _normalize_doubao_response(data: dict) -> dict:
    """
    将火山 Ark chat/completions 响应尽量转为前端可用的 choices 结构。
    若已是多条 message（含 tool）则原样返回；否则从单条 assistant 中尽量提取引用。
    """
    if not data or not isinstance(data, dict):
        return {"choices": []}
    err = data.get("error")
    if err:
        msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
        return {"choices": [], "error": msg}

    choices = data.get("choices")
    if not choices:
        return {"choices": []}

    # 已是 assistant + tool 分条（与讯飞类似）
    roles = [c.get("message", {}).get("role") for c in choices if c.get("message")]
    if "assistant" in roles and "tool" in roles:
        return data

    first = choices[0]
    msg = first.get("message") or {}
    content = msg.get("content") or ""

    outputs = []
    refs = data.get("references") or data.get("web_search_results")
    if isinstance(refs, list):
        for r in refs:
            if isinstance(r, dict):
                outputs.append(
                    {
                        "title": str(r.get("title", r.get("name", ""))),
                        "url": str(r.get("url", r.get("link", ""))),
                    }
                )

    if not outputs:
        annotations = msg.get("annotations") or first.get("annotations")
        if isinstance(annotations, list):
            for a in annotations:
                if isinstance(a, dict) and a.get("type") == "url_citation":
                    cite = a.get("url_citation") or a
                    if isinstance(cite, dict):
                        outputs.append(
                            {
                                "title": str(cite.get("title", "")),
                                "url": str(cite.get("url", "")),
                            }
                        )

    return {
        "choices": [
            {"message": {"role": "assistant", "content": content}},
            {
                "message": {
                    "role": "tool",
                    "tool_calls": [
                        {"type": "web_search", "web_search": {"outputs": outputs}}
                    ],
                }
            },
        ]
    }


def _normalize_ark_responses_api(data: dict) -> dict:
    """将 Responses API（/responses）返回体转为前端可用的 choices 结构。"""
    if not data or not isinstance(data, dict):
        return {"choices": []}
    err = data.get("error")
    if err:
        msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
        return {"choices": [], "error": msg}

    texts: list[str] = []
    refs: list[dict] = []

    def walk(obj):
        if isinstance(obj, dict):
            t = obj.get("type")
            if t == "output_text" and isinstance(obj.get("text"), str):
                texts.append(obj["text"])
            if t == "url_citation":
                cite = obj.get("url_citation") if isinstance(obj.get("url_citation"), dict) else obj
                if isinstance(cite, dict) and cite.get("url"):
                    refs.append(
                        {
                            "title": str(cite.get("title", "")),
                            "url": str(cite.get("url", "")),
                        }
                    )
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for x in obj:
                walk(x)

    walk(data.get("output", []))
    if not texts and data.get("output") in (None, []):
        walk(data)

    content = "".join(texts).strip() or (data.get("output_text") or "") or ""
    # 去重引用
    seen = set()
    uniq_refs = []
    for r in refs:
        u = r.get("url", "")
        if u and u not in seen:
            seen.add(u)
            uniq_refs.append(r)

    return {
        "choices": [
            {"message": {"role": "assistant", "content": content}},
            {
                "message": {
                    "role": "tool",
                    "tool_calls": [
                        {
                            "type": "web_search",
                            "web_search": {"outputs": uniq_refs},
                        }
                    ],
                }
            },
        ]
    }


#========大模型接口========

#秘塔 AI 联网搜索
def get_metaso_api(keyword: str):
    """秘塔 AI 联网搜索（官方 Open API：POST /api/open/search/v2）"""
    url = "https://metaso.cn/api/open/search/v2"
    headers = {
        "Authorization": f"Bearer mk-469D57C55291BFE89EF26A3DD8E7CA2A",
        "Content-Type": "application/json",
    }
    body = {"question": keyword, "lang": "zh", "stream": False}
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=120)
        resp.raise_for_status()
        payload = resp.json()
        data = payload.get("data")
        if data is None:
            return {"choices": [], "error": payload.get("msg") or str(payload)}
        return _normalize_metaso_to_xunfei_shape(data)
    except requests.RequestException as e:
        return {"choices": [], "error": str(e)}

#火山方舟豆包+联网搜索
def get_doubao_ark_api(keyword: str):
    """
    火山方舟豆包 + 联网搜索：使用 Responses API（/responses + tools: web_search）。
    Chat Completions 与 web_search 组合易报 missing tools.function，与官方示例一致走 Responses。
    文档：https://www.volcengine.com/docs/82379/1756990
    """
    base = ('https://ark.cn-beijing.volces.com/api/v3' or "").rstrip("/")
    url = f"{base}/responses"
    payload = {
        "model": 'doubao-seed-1-8-251228',
        "stream": False,
        "tools": [{"type": "web_search"}],
        "input": [
            {
                "role": "user",
                "content": [{"type": "input_text", "text": keyword}],
            }
        ],
    }
    headers = {
        "Authorization": f"Bearer fd42966b-565f-40f1-a857-3465c8d51bde",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=120)
        data = resp.json()
        if resp.status_code >= 400:
            err = data.get("error") if isinstance(data, dict) else None
            msg = err.get("message", resp.text) if isinstance(err, dict) else resp.text
            return {"choices": [], "error": msg}
        return _normalize_ark_responses_api(data)
    except requests.RequestException as e:
        return {"choices": [], "error": str(e)}

#讯飞网络知识检索获取信息
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


#基于ai回答问题（硅基流动互联网模型）
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


#基于aiping平台的大模型回答
def aiping_ai_answer(question):
    """
    调用 aiping 平台进行问答。
    根据提供的示例，采用 OpenAI 库进行流式获取，并拼接完整内容返回。
    """
    from openai import OpenAI
 
    openai_client = OpenAI(
        base_url="https://www.aiping.cn/api/v1",
        api_key="QC-b9b8905d0c03f904041f7ab389ba6f7f-20b1baa3322f30e8450c69207ceddc74"
    )
 
    response = openai_client.chat.completions.create(
        model="DeepSeek-V3.2",
        stream=True,
        extra_body={
            "enable_thinking": False,
            "provider": {
                "only": [], 
                "order": [],
                "sort": None,
                "input_price_range": [],
                "output_price_range": [],
                "input_length_range": [],
                "output_length_range": [],
                "throughput_range": [],
                "latency_range": []
            }
        },
        messages=[
            {"role": "user", "content": str(question)}
        ]
    )
 
    full_content = ""

    for chunk in response:
        if not getattr(chunk, "choices", None):
            continue
        
        reasoning_content = getattr(chunk.choices[0].delta, "reasoning_content", None)
        if reasoning_content:
            print(reasoning_content, end="", flush=True)
 
        content = getattr(chunk.choices[0].delta, "content", None) 
        if content: 
            print(content, end="", flush=True)
            full_content += content
            
    print() # 确保打印换行
    return full_content

#基于内网长城ai回答
def changcheng_ai_answer(question):
    """
    调用长城AI进行问答。
    由于该接口返回的是 Ollama 格式的 NDJSON 流，此处进行同步转换，获取完整回复。
    """
    url = "http://10.68.249.59:33331/api/generate"
    payload = {"prompt": str(question)}
    try:
        # 使用 stream=True 调用
        response = requests.post(url, json=payload, stream=True, timeout=120)
        response.raise_for_status()

        full_content = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode('utf-8'))
                full_content += data.get("response", "")
                if data.get("done"):
                    break

        print(f"长城AI返回: {full_content}")
        return full_content
    except Exception as e:
        print(f"调用长城AI出错: {e}")
        return f"调用长城AI失败: {str(e)}"

#========方法========
#获取联网信息摘要
def fetch_online_infomation_summary(keyword: str, provider: str = "xunfei"):
    """
    联网摘要：provider 可选 xunfei | doubao | metaso
    """
    p = (provider or "xunfei").strip().lower()
    if p in ("doubao", "ark", "volcengine"):
        return get_doubao_ark_api(keyword)
    if p == "metaso":
        return get_metaso_api(keyword)
    return get_xunfei_api(keyword)


# ===  测试入口 ====
if __name__ == "__main__":
    print("测试aipingAI:")
    print(aiping_ai_answer("你好，请介绍你自己"))
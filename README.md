# 科研助手（kyzs）

面向石油/能源行业科研人员的文献管理与 AI 辅助写作平台，前后端分离架构。

## 项目结构

```
kyzs/
├── backend/     # Python FastAPI 后端
├── frontend/    # Vue 3 前端
├── .gitignore
└── README.md    # 本文件
```

## 功能概览

### 后端（`backend/`）

- 文献/专利检索（OilLink、重庆聚合、万方内网），支持年份范围筛选
- 知识库管理（收藏、上传、同步 AnythingLLM 向量库）
- AI 综述报告生成（DeepSeek-V3 等）
- 文档翻译（PDF → 中文 DOCX/PDF）
- **联网信息摘要**（`/get_source/get_online_infomation_summary`）：支持 **讯飞星火**、**火山方舟豆包（联网搜索）**、**秘塔 AI** 三种来源，由前端传入 `provider` 选择

### 前端（`frontend/`）

- Vue 3 + Vite + Element Plus
- 文献/专利合并检索、知识库、翻译、智能问答等
- **网页信息搜索**：可选择搜索源（讯飞 / 豆包 / 秘塔）

---

## 第三方 API 申请与配置说明

以下密钥均配置在 **`backend/.env`**（可参考 `backend/.env.example` 复制）。**不要将真实密钥提交到 Git**（仓库已忽略 `backend/.env`）。

### 1. 秘塔 AI（Metaso）— 联网摘要

1. 打开 [秘塔 AI 搜索 API](https://metaso.cn/search-api/playground)，登录账号。
2. 进入 [API Keys](https://metaso.cn/search-api/api-keys) 页面，按提示**申请 / 创建** API Key（格式一般为 `mk-` 开头）。
3. 在 `backend/.env` 中配置：
   ```env
   metaso_api_key=mk-你的密钥
   ```
4. 前端选择「秘塔 AI」即可使用。官方 HTTP 接口为 `POST https://metaso.cn/api/open/search/v2`（本项目已封装）。

### 2. 火山引擎 · 火山方舟（豆包）— 联网摘要

豆包联网能力通过方舟 **Responses API**（`POST /api/v3/responses`）+ 工具 `web_search` 调用，需同时具备 **API Key** 与 **推理接入点 ID**。

1. 登录 [火山引擎控制台](https://console.volcengine.com/)，进入 **火山方舟**。
2. **获取 API Key**  
   左侧 **系统管理 → API Key 管理** → 创建密钥，复制密钥字符串（形如 UUID）。  
   配置：
   ```env
   doubao_ark_api_key=你的方舟_API_Key
   ```
3. **开通模型**  
   **系统管理 → 开通管理** 中，对需要使用的豆包模型打开开关（如 Doubao-Seed-1.8 等）。
4. **创建推理接入点**  
   **模型推理 → 在线推理 → 自定义推理接入点** → 创建，选择已开通的模型。创建成功后，在列表或详情中复制 **接入点 ID**（**`ep-` 开头**）。  
   配置：
   ```env
   doubao_ark_model=ep-你的接入点ID
   ```
5. **Base URL**（一般不改）  
   默认：`https://ark.cn-beijing.volces.com/api/v3`  
   若使用其他地域/地址，可设置：
   ```env
   doubao_ark_base_url=https://ark.cn-beijing.volces.com/api/v3
   ```

说明：联网搜索属于方舟**内置工具**，无需在「创建接入点」页面单独勾选；后端已按官方方式携带 `tools: [{"type": "web_search"}]`。计费与限流以火山控制台与文档为准。

### 3. 讯飞星火（默认联网摘要）

- 默认「讯飞星火」分支沿用项目内既有讯飞开放平台调用方式；若需改为自己账号，请在控制台申请星火 API 并在 `backend/.env` 配置 `xunfei_api_key`（具体格式见讯飞文档），必要时调整 `services/third_party_source/aichat_api.py` 中 `get_xunfei_api` 的鉴权与模型参数。

---

## 环境变量一览（`backend/config.py`）

| 变量 | 说明 |
|------|------|
| `metaso_api_key` | 秘塔 API Key |
| `doubao_ark_api_key` | 火山方舟 API Key |
| `doubao_ark_model` | 推理接入点 ID（`ep-...`） |
| `doubao_ark_base_url` | 方舟 API 根路径，默认北京 `api/v3` |
| `xunfei_api_key` | 讯飞（可选，视接入方式） |
| `siliconflow_api_key` | SiliconFlow（其他功能） |
| `sql_*` | MySQL（若使用） |

---

## 快速启动

### 后端

需要 **Python 3.10+**（推荐 **3.12**；3.9 无法运行部分类型注解）。

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # 再编辑 .env 填入密钥
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

服务默认：**http://127.0.0.1:8000**

### 前端

```bash
cd frontend
npm install
npm run dev
```

开发服务器默认：**http://localhost:5173/**  
接口基地址默认：`http://127.0.0.1:8000`（见 `frontend/src/api/config.js`，可通过环境变量 `VITE_API_BASE_URL` 或 `vite.config.js` 中的外部配置覆盖）。

---

## 技术栈

| 端 | 技术 |
|----|------|
| 后端 | Python 3.12 / FastAPI / SQLite（`kyzs.db`）等 |
| AI | DeepSeek（SiliconFlow）/ 讯飞星火 / 方舟豆包 Responses API / 秘塔 Open API / AnythingLLM |
| 前端 | Vue 3 / Vite / Element Plus |

更多前端说明见 [frontend/README.md](./frontend/README.md)。

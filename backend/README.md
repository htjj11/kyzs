# 科研助手 — 后端

面向石油/能源行业科研人员的文献管理与 AI 辅助写作平台，后端服务。

> 根目录总览见 [../README.md](../README.md)

## 功能模块

| 模块 | 接口前缀 | 说明 |
|---|---|---|
| 文献/专利检索 | `/get_from_oilink` | 对接 OilLink、重庆聚合、万方（内网）；聚合接口并发查询多源并归一化合并返回 |
| 知识库管理 | `/add_to_knowledge` `/get_knowledge` | 收藏文献/专利/网络信息/文件，同步至 AnythingLLM |
| 综述报告 | `/get_review` | 基于知识库调用 DeepSeek 生成综述，导出 Word |
| 文档翻译 | `/translate` | PDF 上传 → 分段翻译 → 输出中文 DOCX/PDF |
| LLM 对话 | `/llm` | 流式 SSE 对话，基于 AnythingLLM RAG 知识库问答 |
| 系统设置 | `/get_setting` `/system` | 登录、标签管理、提示词模板管理 |

## 聚合检索架构

用户一次搜索 → 后端 `asyncio.gather` **并发** 查询多个数据源 → 归一化字段 → 合并返回统一列表。

| 聚合接口 | 数据源 | 说明 |
|---|---|---|
| `POST /search_all_articles` | OilLink + 聚合 + 万方 | 三源并发，每源默认各取 50 条，全部合并展示 |
| `POST /search_all_patents` | OilLink + 万方 | 双源并发，每源默认各取 50 条，全部合并展示 |

- 各数据源独立容错：任一源超时或报错返回空列表，不影响其他源
- 返回体包含 `counts` 字段，告知每个源各命中多少条
- OilLink 数据自动解析嵌套结构（多语言标题/人员数组/国家代码/datetime 日期）

### 归一化处理

| OilLink 原始字段 | 处理方式 |
|---|---|
| `title: {"en": [...], "zh": [...]}` | 优先取中文，无中文取第一语言 |
| `applicant/inventor: [{"name":"x","sequence":0}]` | 按 sequence 排序，提取姓名逗号连接 |
| `abstract: {"en": [...]}` | 取第一语言全文 |
| `country: "us"` | 映射为中文国家名称 |
| `app_date/pub_date: datetime` | 截取为 `YYYY-MM-DD` 格式 |

### 年份范围过滤策略

| 数据源 | 过滤方式 |
|---|---|
| OilLink 文献/专利 | API 不支持日期参数，后端获取后按 `year`/`app_date` 字段过滤 |
| 聚合文献 | 聚合 API 仅支持精确单年，后端获取全量后按 `年份` 字段过滤 |
| 万方文献/专利 | API 层 `Date within` 查询 + 后端兜底二次过滤 |

## 技术栈

- **运行时**：Python 3.12
- **框架**：FastAPI + Uvicorn
- **数据库**：MySQL 8（pymysql + DBUtils 连接池）
- **安全**：参数化 SQL 查询防注入，Pydantic Settings 管理敏感配置
- **AI 服务**：SiliconFlow DeepSeek-V3 / 讯飞星火 / AnythingLLM（本地 RAG）
- **文档处理**：pypandoc / python-docx / pdf2docx / pypdf / python-pptx

## 目录结构

```
backend/
├── app/                             主程序目录
│   ├── main.py                      FastAPI 应用工厂，注册所有路由
│   ├── config.py                    Pydantic Settings 配置，读取 .env
│   ├── core/
│   │   ├── database.py              MySQL 连接池客户端
│   │   └── utils.py                 通用工具函数
│   ├── services/
│   │   ├── literature_service.py    文献/专利/综述/大模型调用
│   │   ├── translate_service.py     文档翻译
│   │   └── chat_service.py          AnythingLLM / LLM 对话
│   └── routers/
│       ├── literature.py            检索接口（聚合多源 + 归一化 + 年份过滤）
│       ├── knowledge_add.py         收藏接口
│       ├── knowledge.py             知识库管理接口
│       ├── review.py                综述报告接口
│       ├── settings.py              系统设置接口
│       ├── translate.py             翻译接口
│       ├── auth.py                  登录接口
│       └── chat.py                  LLM 对话接口
│
├── tests/                           pytest 测试用例
├── file/                            翻译任务输出文件（docx/pdf）
├── oillink接口文档/                  第三方接口参考文档
├── kyzs.sql                         数据库建表脚本
├── run.py                           启动入口（python run.py）
├── requirements.txt                 Python 依赖
├── .env                             本地环境变量（不提交 git）
├── .env.example                     环境变量模板
└── README.md                        本文件
```

## 快速开始

### 1. 环境要求

- Python 3.12+
- MySQL 8.0+
- [AnythingLLM](https://anythingllm.com)（本地运行，默认端口 3001）
- pandoc（Markdown 转 Word，需单独安装）

### 2. 安装依赖

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. 初始化数据库

```bash
mysql -u root -p
# 在 MySQL 中执行：
# CREATE DATABASE kyzs;
# exit;
mysql -u root -p kyzs < kyzs.sql
```

### 4. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填入数据库密码和各 API Key：

```ini
SQL_PASSWORD=your_db_password
SILICONFLOW_API_KEY=sk-xxxxxxxx
XUNFEI_API_KEY=AppId:APISecret
JUHE_TOKEN=xxxxxxxx
ANYTHINGLLM_API_KEY=XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX
```

### 5. 启动服务

```bash
python run.py
```

服务启动后：
- API 地址：`http://localhost:8000`
- 交互式文档：`http://localhost:8000/docs`

## API Key 获取

| 服务 | 获取地址 |
|---|---|
| SiliconFlow（DeepSeek-V3） | https://siliconflow.cn → 控制台 → API Key |
| 讯飞星火 | https://console.xfyun.cn → 我的应用 |
| AnythingLLM | 本地服务 → 设置 → API Key |
| 重庆聚合文献 | 联系服务提供方 |
| 万方（内网） | 企业内网访问，无需 Key |

## 注意事项

- **万方接口**（`10.68.16.2`）依赖企业内网，外网环境下该接口不可用
- **翻译模块**中 `docx2pdf` 在 Windows 上依赖 Microsoft Word，Linux/macOS 需安装 LibreOffice
- `.env` 文件包含密钥，已加入 `.gitignore`，**请勿提交到 git**
- `file/` 目录存储翻译输出文件，建议定期清理

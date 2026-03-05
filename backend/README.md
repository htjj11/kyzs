# 科研助手 — 后端

面向石油/能源行业科研人员的文献管理与 AI 辅助写作平台，后端服务。

> 根目录总览见 [../README.md](../README.md)

## 功能模块

| 模块 | 接口前缀 | 说明 |
|---|---|---|
| 文献/专利检索 | `/get_from_oilink` | 对接 OilLink、重庆聚合、万方（内网）四个数据源 |
| 知识库管理 | `/add_to_knowledge` `/get_knowledge` | 收藏文献/专利/网络信息/文件，同步至 AnythingLLM |
| 综述报告 | `/get_review` | 基于知识库调用 DeepSeek 生成综述，导出 Word |
| 文档翻译 | `/translate` | PDF 上传 → 分段翻译 → 输出中文 DOCX/PDF |
| LLM 对话 | `/llm` | 流式 SSE 对话，基于 AnythingLLM RAG 知识库问答 |
| 系统设置 | `/get_setting` `/system` | 登录、标签管理、提示词模板管理 |

## 技术栈

- **运行时**：Python 3.12
- **框架**：FastAPI + Uvicorn
- **数据库**：MySQL 8（pymysql）
- **AI 服务**：SiliconFlow DeepSeek-V3 / 讯飞星火 / AnythingLLM（本地 RAG）
- **文档处理**：pypandoc / python-docx / pdf2docx / pypdf / python-pptx

## 目录结构

> `🆕` = 重构新建　`♻️` = 由旧文件迁移改写　`📦` = 原有文件保持不变

```
backend/
├── app/                             🆕 新建包，重构后的主程序目录（可按需改名为 src/）
│   ├── main.py                      🆕 FastAPI 应用工厂，注册所有路由（原 kyzs.py 拆分）
│   ├── config.py                    ♻️ 统一配置，读取 .env（原 config.py 升级为 Pydantic Settings）
│   ├── core/                        🆕 新建，核心基础设施层
│   │   ├── database.py              ♻️ MySQL 客户端（原 api/sql_role.py 迁移）
│   │   └── utils.py                 ♻️ 通用工具函数（原 api/tools.py 迁移）
│   ├── services/                    🆕 新建，业务逻辑层（对应原 api/ 目录）
│   │   ├── literature_service.py    ♻️ 文献/专利/综述/大模型（原 api/api_bg.py 迁移）
│   │   ├── translate_service.py     ♻️ 文档翻译（原 api/api_fy.py 迁移）
│   │   └── chat_service.py          ♻️ AnythingLLM / LLM 对话（原 api/api_chat.py 迁移）
│   └── routers/                     🆕 新建，路由层（对应原 subapi/ 目录）
│       ├── literature.py            ♻️ 检索接口（原 subapi/get_from_oilink.py 迁移）
│       ├── knowledge_add.py         ♻️ 收藏接口（原 subapi/add_to_knowledge.py 迁移）
│       ├── knowledge.py             ♻️ 知识库管理接口（原 subapi/get_knowledge.py 迁移）
│       ├── review.py                ♻️ 综述报告接口（原 subapi/get_review.py 迁移）
│       ├── settings.py              ♻️ 系统设置接口（原 subapi/get_setting.py 迁移）
│       ├── translate.py             ♻️ 翻译接口（原 subapi/translate.py 迁移）
│       ├── auth.py                  ♻️ 登录接口（原 subapi/system.py 迁移）
│       └── chat.py                  ♻️ LLM 对话接口（原 subapi/llm_chat.py 迁移）
│
├── api/                             📦 原有业务逻辑层，保持不变
│   ├── api_bg.py
│   ├── api_fy.py
│   ├── api_chat.py
│   ├── sql_role.py
│   └── tools.py
├── subapi/                          📦 原有路由层，保持不变
│   ├── get_from_oilink.py
│   ├── add_to_knowledge.py
│   ├── get_knowledge.py
│   ├── get_review.py
│   ├── get_setting.py
│   ├── translate.py
│   ├── system.py
│   └── llm_chat.py
│
├── file/                            📦 翻译任务输出文件（docx/pdf）
├── kyzs.sql                         📦 数据库建表脚本
├── kyzs.py                          📦 原启动入口（兼容旧版）
├── run.py                           🆕 新启动入口（python run.py）
├── requirements.txt                 ♻️ Python 依赖（新增 pydantic-settings）
├── .env                             🆕 本地环境变量，含真实密钥（不提交 git）
├── .env.example                     🆕 环境变量模板（提交 git，供参考）
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
pip install -r requirements.txt
```

### 3. 初始化数据库

```bash
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
- `.env` 文件包含密钥，已加入根目录 `.gitignore`，**请勿提交到 git**
- `file/` 目录存储翻译输出文件，建议定期清理

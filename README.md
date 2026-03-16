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

## 模块说明

### 后端（`backend/`）
- 文献/专利检索（OilLink、重庆聚合、万方内网），支持年份范围筛选
- 知识库管理（收藏、上传、同步 AnythingLLM 向量库）
- AI 综述报告生成（DeepSeek-V3）
- 文档翻译（PDF → 中文 DOCX/PDF）
- LLM 流式对话（AnythingLLM RAG）

详见 [backend/README.md](./backend/README.md)

### 前端（`frontend/`）
- 基于 Vue 3 + Vite + Element Plus 构建
- 文献检索：一次搜索同时查询 OilLink / 聚合 / 万方 三个数据源，结果归一化合并展示
- 专利检索：一次搜索同时查询 OilLink / 万方 两个数据源，结果归一化合并展示
- 支持年份范围筛选，来源标签标识每条结果的数据源

## 快速启动

**后端：**
```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
cp .env.example .env   # 填入配置
pip install -r requirements.txt
python run.py
```

**前端：**
```bash
cd frontend
npm install
npm run dev
```

## 技术栈

| 端 | 技术 |
|---|---|
| 后端 | Python 3.12 / FastAPI / MySQL / DBUtils 连接池 |
| AI | DeepSeek-V3 / 讯飞星火 / AnythingLLM |
| 前端 | Vue 3 / Vite / Element Plus |

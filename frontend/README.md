# 科研助手 (KYZS) 前端项目

这是一个基于 Vue 3 和 Vite 构建的“科研助手” Web 前端项目，旨在为科研人员提供文献检索、专利检索、知识库管理、文本与文档翻译以及智能问答等一站式服务。

## 🛠️ 技术栈

本项目采用了现代化的前端技术栈构建：

- **核心框架**：[Vue 3](https://vuejs.org/) (使用 `<script setup>` 组合式 API)
- **构建工具**：[Vite](https://vitejs.dev/) - 极速的前端构建工具，提供极速的冷启动和热更新
- **UI 组件库**：[Element Plus](https://element-plus.org/) - 基于 Vue 3 的组件库，提供丰富的业务组件
- **路由管理**：[Vue Router 4](https://router.vuejs.org/) - 官方的路由管理器
- **状态管理**：[Pinia](https://pinia.vuejs.org/) - Vue 的专属状态管理库（Vuex 的替代方案）
- **网络请求**：[Axios](https://axios-http.com/) - 基于 Promise 的 HTTP 库
- **富文本及 Markdown**：集成 [Tiptap](https://tiptap.dev/) 和 [md-editor-v3](https://imzbf.github.io/md-editor-v3/)，提供强大的编辑器支持

## ✨ 主要功能模块

- **🔐 登录鉴权**：系统登录与用户认证。
- **🔍 检索功能**：
  - **文献搜索** (`literatureSearch`)：快速查找相关学术文献。
  - **专利检索** (`patentSearch`)：检索相关技术专利。
  - **网页信息搜索** (`webinfoSearch`)：进行全网信息检索。
- **📚 知识库管理**：
  - **资料上传** (`fileUpload`)：支持将多文件上传至知识库系统。
  - **知识库查看** (`zskck`, `zsck`)：浏览及管理已经构建的个人或团队知识库内容。
- **🌐 翻译助手**：
  - **文本翻译** (`wbfy`)：支持实时的长短文本翻译。
  - **文档翻译** (`wdfy`)：支持文档文件的快速翻译处理。
  - **词库管理** (`ckgl`)：管理个人翻译词库。
- **💬 智能问答** (`wenda`)：集成智能化对话与问答系统，辅助科研思考与解答。
- **⚙️ 其他功能**：
  - **数据库管理** (`db_manage`, `all_db`)：后台数据管理功能。
  - **高级编辑器** (`new_editor`)：支持复杂排版与创作。
  - **全局设置** (`qtsz`)：系统偏好设置等。

## 🚀 快速开始

### 1. 环境准备

确保你的机器上安装了 [Node.js](https://nodejs.org/) (建议版本 16.0 或更高)。

### 2. 安装依赖

```bash
npm install
```

### 3. 本地开发服务器启动

```bash
npm run dev
```

该命令会启动一个基于 Vite 的本地开发服务器，并支持热更新（HMR）。

### 4. 生产环境构建

```bash
npm run build
```

构建完成后，打包生成的文件将存放在 `dist` 目录中，可直接部署至 Nginx、Apache等 Web 服务器。

### 5. 本地预览构建结果

```bash
npm run preview
```

## 📁 目录结构说明

```text
frontend/
├── src/
│   ├── api/            # 集中管理 API 接口定义和 axios 请求
│   ├── assets/         # 静态资源文件（图片、全局样式等）
│   ├── components/     # 业务组件与视图页面 (报告、问答、翻译等)
│   ├── router/         # 路由配置文件
│   ├── utils/          # 全局工具函数 (如：认证拦截等)
│   ├── App.vue         # 根组件
│   └── main.js         # 项目入口文件，应用挂载与插件注册
├── public/             # 公共静态资源
├── package.json        # 项目依赖清单及执行脚本
├── vite.config.js      # Vite 构建配置文件
└── README.md           # 项目说明文档
```

## IDE 推荐配置

推荐使用 [VSCode](https://code.visualstudio.com/) 配合 [Vue - Official](https://marketplace.visualstudio.com/items?itemName=Vue.volar) 扩展插件以获得最佳的开发体验和 TypeScript/Vue 支持。

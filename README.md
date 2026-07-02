# 企业级 AI 知识工单助手

> **Enterprise AI Knowledge Work Order Assistant** — 从 0 开发一个企业级 AI 知识工单助手：前端 + 后端 + Agent + RAG + 部署完整实战。

一个完整的企业级 AI 助手系统，集成了智能对话、知识库管理、工单处理、人工审核、Agent 流程可视化等核心功能。

---

## 📋 项目概览

```text
企业级 AI 知识工单助手
├── 前端管理后台          — Vue 3 + Element Plus
├── 后端服务              — FastAPI + LangChain
├── AI Agent              — LangGraph 流程编排
├── RAG 检索增强生成       — 向量检索 + 混合检索
└── 基础设施              — PostgreSQL / Redis / Qdrant
```

### 核心能力

| 能力 | 说明 |
|------|------|
| 💬 AI 智能对话 | 结构化回答、意图识别、流式输出 |
| 📚 知识库管理 | 文档上传、解析、切片、向量化 |
| 🔧 工具调用 | 订单查询、工单处理、业务系统集成 |
| 👤 人工审核 | 高风险操作审批（Human-in-the-Loop） |
 | 🔍 RAG 检索调试 | 检索策略对比、召回效果分析 |
| 📊 评估报告 | 准确率、召回率、失败样本分析 |
| 🔐 权限控制 | 多角色菜单与按钮级权限 |
| 📜 Agent 执行追踪 | 执行步骤可视化、失败恢复与重试 |

---

## 🏗️ 技术栈

### 前端

| 技术 | 用途 |
|------|------|
| **Vue 3** | 前端框架 |
| **Vite** | 构建工具 |
| **Element Plus** | UI 组件库 |
| **Pinia** | 状态管理 |
| **Vue Router** | 路由管理 |
| **Axios** | HTTP 请求 |
| **ECharts** | 数据可视化 |
| **markdown-it** | Markdown 渲染 |
| **highlight.js** | 代码高亮 |

### 后端

| 技术 | 用途 |
|------|------|
| **FastAPI** | Web 框架 |
| **LangChain** | LLM 应用框架 |
| **LangGraph** | Agent 流程编排 |
| **Pydantic** | 数据验证 |
| **PostgreSQL** | 关系数据库 |
| **Redis** | 缓存 / 会话管理 |
| **Qdrant / pgvector** | 向量数据库 |
| **LangSmith** | LLM 可观测性 |

---

## 📁 项目结构

```text
enterprise-ai-assistant/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── main.py            # FastAPI 入口
│   │   ├── api/               # API 路由
│   │   ├── agents/            # Agent 逻辑
│   │   ├── rag/               # RAG 检索服务
│   │   ├── schemas/           # Pydantic 模型
│   │   └── tools/             # 工具函数
│   ├── tests/                 # 测试
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # 前端管理后台
│   ├── src/
│   │   ├── api/               # API 接口封装
│   │   ├── views/             # 页面组件
│   │   ├── components/        # 通用组件
│   │   ├── router/            # 路由配置
│   │   ├── stores/            # Pinia 状态管理
│   │   └── main.ts            # 入口文件
│   ├── public/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── vite.config.ts
│   └── package.json
│
├── deploy/                     # 部署配置
│   ├── nginx/
│   ├── postgres/
│   └── qdrant/
│
├── docker-compose.yml          # 一键启动
├── .env.example                # 环境变量示例
└── README.md
```

---

## 🖥️ 页面清单

| 路由 | 页面 | 功能 |
|------|------|------|
| `/login` | 登录页 | 用户认证 |
| `/chat` | AI 对话工作台 | 智能对话、工具调用、上下文面板 |
| `/documents` | 知识库管理 | 文档上传、解析状态、索引管理 |
| `/rag-debug` | 检索调试 | 检索策略对比、召回效果分析 |
| `/tickets` | 工单列表 | 工单查询与处理 |
| `/tickets/:id` | 工单详情 | 业务信息卡片、AI 分析结果 |
| `/approvals` | 人工审核 | 高风险操作审批 |
| `/traces` | Agent 执行记录 | 执行步骤时间线、失败恢复 |
| `/evaluations` | 评估报告 | 准确率图表、失败样本分析 |
| `/settings` | 系统配置 | 模型、知识库、权限配置 |
| `/no-permission` | 无权限页面 | 权限不足提示 |

---

## 🚀 快速开始

### 环境要求

- **Node.js** >= 18
- **Python** >= 3.10
- **PostgreSQL** >= 15
- **Redis** >= 7
- **Docker** & **Docker Compose**（可选）

### 1. 克隆项目

```bash
git clone <repository-url>
cd enterprise-ai-assistant
```

### 2. 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库、API Key 等

# 启动服务
python -m app.main
```

后端服务默认运行在 `http://localhost:8080`。

### 3. 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端开发服务器默认运行在 `http://localhost:5173`。

### 4. Docker 一键启动

```bash
docker-compose up -d
```

---

## 🗓️ 开发路线图

### 第 1 周：AI 助手前后端基础

| 天数 | 内容 | 产出 |
|------|------|------|
| Day 1 | 需求分析、项目搭建、架构设计 | 项目骨架 |
| Day 2 | 聊天页面 + 对话接口 | 可聊天的 AI 页面 |
| Day 3 | 结构化回答 + 卡片展示 | 答案卡片组件 |
| Day 4 | 工具调用（查订单） | 工具调用流程 |
| Day 5 | Agent 工作台 + 上下文面板 | 业务工作台 |

### 第 2 周：RAG 知识库

| 天数 | 内容 | 产出 |
|------|------|------|
| Day 6 | 文档上传与管理页面 | 知识库管理 |
| Day 7 | 文档切片、向量化、状态追踪 | 处理状态展示 |
| Day 8 | 知识库问答 | RAG 检索回答 |
| Day 9 | 引用来源展示 | 来源展开查看 |
| Day 10 | 检索调试页面 | 检索效果对比 |

### 第 3 周：业务处理与审批

| 天数 | 内容 | 产出 |
|------|------|------|
| Day 11 | 意图识别 | 任务类型展示 |
| Day 12 | 多业务系统查询 | 业务信息卡片 |
| Day 13 | 会话管理 | 会话列表与切换 |
| Day 14 | 用户权限控制 | 权限管理 |
| Day 15 | 人工审批页面 | 审批工作流 |

### 第 4 周：上线与部署

| 天数 | 内容 | 产出 |
|------|------|------|
| Day 16 | Agent 执行步骤可视化 | 执行时间线 |
| Day 17 | 失败恢复与重试 | 错误处理机制 |
| Day 18 | SSE 流式输出 | 实时流式展示 |
| Day 19 | 评估报告页面 | 数据可视化报表 |
| Day 20 | Docker 部署 | 完整系统部署 |

---

## 🔧 核心功能模块

### AI 对话工作台

三栏式布局：左侧会话列表 | 中间聊天区域 | 右侧上下文面板。

- 支持流式输出，实时展示 AI 思考过程
- 结构化答案卡片（意图标签、置信度、建议操作）
- 工具调用过程可视化
- 引用来源展开查看

### 知识库管理

- 支持多种格式文档上传（PDF、Markdown、Word、Excel、CSV）
- 文档处理状态追踪（上传 → 解析 → 切片 → 向量化 → 可检索）
- 检索调试页面，支持多种检索策略对比

### 工单处理

- 工单列表与详情查看
- 多业务系统信息聚合（用户、订单、支付、物流）
- AI 分析建议与人工确认

### 人工审核

- 高风险操作（退款、改单、通知等）拦截审批
- 审核详情查看（AI 建议、工具参数）
- 通过 / 拒绝 / 修改后通过

### Agent 执行追踪

- LangGraph 流程步骤可视化
- 节点状态（运行中、成功、失败）
- 失败节点重试与恢复

---

## 📊 评估体系

- 回答准确率统计
- 工具调用成功率
- RAG 召回命中率
- 人工审核触发率分析
- 失败样本明细与 Trace 关联

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来完善项目。

---

## 📄 许可证

本项目仅供学习参考使用。

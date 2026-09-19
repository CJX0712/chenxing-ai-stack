# 晨星 AI Stack · 系统架构

> 作者：晨星 ｜ 版本：1.0.0 ｜ 定位：企业 RAG/Agent 平台（模块化、版本锁定、可一键复现）

## 1. 设计原则

| 原则 | 落地方式 |
|------|----------|
| 单一职责 | 每个模块只做一件事，接口显式声明 |
| 接口契约 | 模块间通过 Python 类型 / HTTP-JSON 通信，依赖只向下 |
| 可独立验证 | 每个模块在 `fake`/`memory` 模式下可单测，无需外部服务 |
| 复用优先 | 核心能力全部基于业界领先开源，不自研重复轮子 |
| 可复现 | `uv.lock` 锁版本 + `docker-compose.yml` 镜像打 tag |

## 2. 模块划分与接口

| 模块 | 文件 | 职责 | 对外接口 | 复用开源 |
|------|------|------|----------|----------|
| M1 ingest | `app/core/ingest.py` | 文档加载/切片 | `ingest_text()` / `ingest_file()` | pypdf / python-docx |
| M2 embed | `app/core/embed.py` | 文本向量化 | `embed(texts) -> vectors` | Ollama `/api/embed` |
| M3 vector-store | `app/core/vector_store.py` | 向量存取/检索 | `upsert()` / `search()` | Qdrant |
| M4 rerank | `app/core/rerank.py` | 召回重排 | `rerank(query, docs, top_k)` | bge-reranker（懒加载） |
| M5 llm | `app/core/llm.py` | LLM 推理 | `generate(messages) -> str` | Ollama `/api/chat` |
| M6 orchestrator | `app/core/orchestrator.py` | 智能体回路 | `run(query, top_k, use_rag)` | LangGraph |
| RAG 组合层 | `app/core/rag.py` | 拼装 M2+M3+M4 | `add_documents()` / `retrieve()` | — |
| M7 api-gateway | `app/api/*` + `app/main.py` | 路由/鉴权/限流 | REST/JSON (OpenAPI) | FastAPI + PyJWT |
| M8 observability | `app/core/observability.py` | 追踪/指标 | `span(name)` 上下文管理器 | OpenTelemetry |
| web | `web/` | 聊天调试台 | 浏览器 | React + Vite |

## 3. 调用链路

```
┌─────────┐      ┌─────────────┐
│   web   │─────▶│ api-gateway │  (FastAPI + JWT 鉴权)
└─────────┘      └──────┬──────┘
                        │
                  ┌─────▼──────┐
                  │orchestrator│  (LangGraph: retrieve → generate)
                  └──┬─────┬───┘
           ┌─────────▼──┐   ┌─▼────────┐
           │    rag     │   │   llm    │  (Ollama)
           │(embed+store│   └──────────┘
           │ +rerank)   │
           └──┬──┬──┬───┘
         embed│  │store
          (M2)│  │(M3/Qdrant)
              │  │
           rerank(M4)

  observability(M8) 经 OTLP 旁路包裹全链路，缺依赖时自动退化为无操作
```

## 4. 技术复用清单

- **FastAPI / Uvicorn** — 异步 API 网关
- **LangGraph** — 状态图编排（retrieve→generate 回路；未安装时降级为等价顺序执行）
- **Qdrant** — 向量数据库（`:memory:` 模式用于单测，服务端模式用于生产）
- **Ollama** — 本地 LLM + Embedding 推理（OpenAI 兼容协议，免云密钥、可离线）
- **Pydantic / pydantic-settings** — 配置与数据契约
- **PyJWT** — 鉴权
- **httpx** — 对外 HTTP 调用（Ollama）
- **OpenTelemetry** — 可观测（可选启用）
- **pypdf / python-docx** — 文档摄入

## 5. 降级策略（保证「无重依赖也能跑」）

| 能力 | 默认 | 真实模式 |
|------|------|----------|
| LLM (M5) | `fake`（占位回答） | `real`（Ollama） |
| Embed (M2) | `fake`（哈希向量） | `real`（Ollama nomic-embed-text） |
| Vector (M3) | `memory`（进程内） | `qdrant`（服务端） |
| Rerank (M4) | `none`（保序） | `cross-encoder`（懒加载，不拖累安装） |
| 编排 (M6) | LangGraph，缺失则顺序执行 | 同左 |
| 可观测 (M8) | 无操作 | OTel 导出 |

## 6. 目录结构

```
chenxing-ai-stack/
├── docker-compose.yml      # 一体编排：ollama + qdrant + backend + web
├── Makefile                # bootstrap/install/test/server/up/down/ingest/chat
├── .env.example            # 全部环境变量样例
├── backend/
│   ├── pyproject.toml      # 依赖范围（版本锁定）
│   ├── uv.lock             # 精确锁版本（可复现）
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py         # 入口装配
│   │   ├── config.py       # 配置（单一事实来源）
│   │   ├── schemas.py      # 数据契约
│   │   ├── security.py     # JWT
│   │   ├── api/            # 路由
│   │   └── core/           # M1–M8 模块
│   └── tests/              # 逐模块单测（12 项全绿）
└── web/                    # React + Vite 调试台
```

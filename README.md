# 晨星 AI Stack

> 企业 RAG/Agent 平台 · 模块化 · 版本锁定 · 一键可复现
> 作者：**晨星**

一套基于业界领先开源技术、端到端可实际运行的 AI 应用开发运行环境。覆盖
「摄入 → 向量化 → 存储 → 召回 → 重排 → 编排 → 推理 → 服务 → 观测」全链路，
每个模块单一职责、接口明确、可独立验证，并协同组成完整可运行链路。

## 特性

- ✅ **复用优先**：FastAPI · LangGraph · Qdrant · Ollama · OpenTelemetry，不自研
- ✅ **模块化**：M1–M8 + 前端，单一职责，接口契约化
- ✅ **可独立验证**：`fake`/`memory` 模式单测全绿（12/12），无需外部服务
- ✅ **可复现**：`uv.lock` 精确锁版本 + `docker-compose.yml` 镜像打 tag
- ✅ **可降级**：缺模型/缺依赖时自动退化，保证链路跑通
- ✅ **一键部署**：`make up` 或 `uv sync` + `uv run uvicorn`

## 快速开始

```bash
# 本地开发
cd backend && uv sync && uv run uvicorn app.main:app --reload
cd web && npm install && npm run dev      # http://localhost:5173

# 或 Docker 一体
cp .env.example .env                       # 按需改 LLM_MODE=real 等
docker compose up -d --build
```

## 文档

- [ARCHITECTURE.md](./ARCHITECTURE.md) — 系统架构与模块接口
- [DEPLOYMENT.md](./DEPLOYMENT.md) — 部署指南
- [USAGE.md](./USAGE.md) — 使用指南

## 目录

```
backend/   Python 服务（FastAPI + 核心模块 + 测试）
web/       React + Vite 调试台
docker-compose.yml / Makefile / .env.example   编排与配置
```

© 晨星 · MIT License

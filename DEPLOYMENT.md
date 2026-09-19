# 晨星 AI Stack · 部署指南

> 作者：晨星 ｜ 两种形态：Docker 一体部署（生产/演示） · 本地 uv 开发部署

## 一、前置要求

| 形态 | 要求 |
|------|------|
| Docker 一体 | Docker Engine + Compose v2；真实推理需可拉取 Ollama 模型（约 5–8 GB 磁盘） |
| 本地开发 | Python ≥ 3.11、Node ≥ 18；同理真实推理需 Ollama 已启动 |
| 硬件提示 | 16 GB RAM 可跑 `qwen2.5:7b` q4 + Qdrant；无独显亦可，吞吐适中 |

## 二、方式 A：Docker 一体部署（推荐）

```bash
# 1. 准备环境变量（真实推理）
cp .env.example .env
# 编辑 .env：LLM_MODE=real / EMBED_MODE=real / VECTOR_MODE=qdrant

# 2. 启动全部服务
docker compose up -d --build

# 3. 首次拉取模型（仅真实模式需要）
docker compose exec ollama ollama pull qwen2.5:7b
docker compose exec ollama ollama pull nomic-embed-text

# 4. 健康检查
curl http://localhost:8000/health
# 前端：http://localhost:5173
```

> 说明：`qdrant` 健康检查用 lenient 写法，`docker compose up` 不会卡在等待；真实健康以 `:6333/health` 为准。

## 三、方式 B：本地 uv 开发部署

```bash
# 后端
cd backend
uv sync --extra rerank          # 安装依赖（含可选 rerank）
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 前端（另一终端）
cd web
npm install
npm run dev                     # http://localhost:5173（已代理 /v1 到 8000）
```

## 四、关键环境变量（见 `.env.example`）

| 变量 | 说明 | 默认 |
|------|------|------|
| `LLM_MODE` | `fake` / `real` | fake |
| `EMBED_MODE` | `fake` / `real` | fake |
| `VECTOR_MODE` | `memory` / `qdrant` | memory |
| `RERANK_MODE` | `none` / `cross-encoder` | none |
| `OLLAMA_BASE_URL` | Ollama 地址 | http://localhost:11434 |
| `QDRANT_URL` | Qdrant 地址 | http://localhost:6333 |
| `AUTH_ENABLED` | 是否开启 JWT 鉴权 | false |
| `OTEL_ENABLED` | 是否启用 OpenTelemetry | false |

## 五、构建可复现保证

- `backend/uv.lock`：由 `uv lock` 生成，精确锁定全部 Python 依赖版本
- `docker-compose.yml`：各镜像均打固定 tag（ollama 0.5.7 / qdrant 1.13.0）
- 干净环境执行 `uv sync` 或 `docker compose up --build` 即可一键复现

## 六、常见故障排查

| 现象 | 排查 |
|------|------|
| 后端起不来，报连不上 Qdrant | `VECTOR_MODE` 设为 `memory` 先验证链路；生产再切 `qdrant` 并确认服务健康 |
| 真实模式返回空/报错 | `curl localhost:11434/api/tags` 确认模型已 `ollama pull` |
| 维度不匹配 (Qdrant) | `EMBED_DIM` 须与真实 embedding 维度一致（nomic-embed-text=768） |
| 拉取模型慢 | 仅首次；可做镜像预置或换更小的 `qwen2.5:3b` |

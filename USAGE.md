# 晨星 AI Stack · 使用指南

> 作者：晨星 ｜ 覆盖：一键命令、API 调用、前端、鉴权、验证

## 一、一键命令（Makefile）

```bash
make bootstrap     # = uv sync（可选 --extra rerank）
make server        # 启动后端（热重载）
make test          # 跑全部 pytest（fake/memory 模式）
make up            # docker compose 一体启动
make down          # 停止并移除容器
make ingest        # 灌入一条种子语料
make chat          # 向 /v1/chat 发一条提问
```

## 二、API 示例

### 健康检查
```bash
curl http://localhost:8000/health
# => {"status":"ok","llm_mode":"fake", ...}
```

### 摄入文本
```bash
curl -X POST http://localhost:8000/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{"text":"晨星是深圳前端工程师，负责企业协同平台 v3.2 的 React 组件重构。","source":"seed"}'
# => {"ingested": 3, "collection":"chenxing_docs"}
```

### 对话（RAG）
```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"晨星负责什么"," "top_k":3}'
# => {"answer":"...","context":["..."],"model":"qwen2.5:7b"}
```

### 摄入文件
```bash
curl -X POST http://localhost:8000/v1/ingest/file -F "file=@docs/sample.md"
```

## 三、前端调试台

```bash
cd web && npm install && npm run dev
# 打开 http://localhost:5173
```
输入框输入问题回车即可；界面展示回答与「召回上下文」，直观验证 RAG 链路。

## 四、可选鉴权（JWT）

1. `.env` 设 `AUTH_ENABLED=true` 与 `JWT_SECRET`
2. 用 `app.security.create_access_token("user")` 签发（或实现 `/v1/token` 端点）
3. 请求头携带 `Authorization: Bearer <token>`

## 五、验证（CI / 本地）

```bash
cd backend
uv run pytest -q
# 12 passed —— 覆盖 ingest/embed/store/rerank/llm/orchestrator/api
```

所有模块均可在无 Ollama / 无 Qdrant 的 `fake`+`memory` 模式下独立验证，确保干净环境可复现、可诊断。

## 六、从 fake 切到真实推理（本地）

```bash
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
# 修改 .env：LLM_MODE=real, EMBED_MODE=real, VECTOR_MODE=qdrant
# 重启后端
```

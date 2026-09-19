.PHONY: bootstrap install test server up down logs ingest chat fmt

bootstrap: install

install:
	uv sync --extra rerank || uv sync

test:
	cd backend && uv run pytest -q

server:
	cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

up:
	docker compose up -d --build
	@echo "等待服务就绪: docker compose ps"

down:
	docker compose down

logs:
	docker compose logs -f backend

ingest:
	curl -X POST http://localhost:8000/v1/ingest -H "Content-Type: application/json" -d '{"text":"晨星是深圳前端工程师，负责企业协同平台 v3.2 的 React 组件重构。","source":"seed"}'

chat:
	curl -X POST http://localhost:8000/v1/chat -H "Content-Type: application/json" -d '{"query":"晨星负责什么","top_k":3}'

fmt:
	cd backend && uv run ruff format app || true

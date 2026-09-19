"""M6 编排层。单一职责：串联 retrieve -> generate 组成 Agent 回路。
优先复用 LangGraph 编译状态图；若环境未装 LangGraph 则降级为等价顺序执行，
保证「复用业界领先开源」与「无依赖也能跑」二者兼得。
接口: run(query, top_k, use_rag) -> {"answer": str, "context": List[str]}
"""
from typing import List, TypedDict

from app.config import get_settings
from app.core.llm import LLM
from app.core.observability import span
from app.core.rag import get_rag

try:
    from langgraph.graph import END, StateGraph

    _HAVE_LANGGRAPH = True
except Exception:  # pragma: no cover - 可选依赖
    _HAVE_LANGGRAPH = False


class State(TypedDict):
    query: str
    top_k: int
    context: List[str]
    answer: str


def _retrieve(state: State) -> dict:
    ctx = get_rag().retrieve(state["query"], state["top_k"])
    return {"context": ctx}


def _generate(state: State) -> dict:
    llm = LLM()
    sys_msg = {
        "role": "system",
        "content": "你是企业知识助手，仅依据给定的上下文回答；无相关信息时明确说明无法回答。",
    }
    ctx_block = "\n".join(state["context"]) or "（无检索上下文）"
    user_msg = {
        "role": "user",
        "content": f"上下文:\n{ctx_block}\n\n问题: {state['query']}",
    }
    return {"answer": llm.generate([sys_msg, user_msg])}


def _build():
    if not _HAVE_LANGGRAPH:
        return None
    g = StateGraph(State)
    g.add_node("retrieve", _retrieve)
    g.add_node("generate", _generate)
    g.set_entry_point("retrieve")
    g.add_edge("retrieve", "generate")
    g.add_edge("generate", END)
    return g.compile()


_graph = _build()


def run(query: str, top_k: int = 5, use_rag: bool = True) -> dict:
    with span("orchestrator.run"):
        if not use_rag:
            ans = LLM().generate([{"role": "user", "content": query}])
            return {"answer": ans, "context": []}
        if _graph is not None:
            out = _graph.invoke(
                {"query": query, "top_k": top_k, "context": [], "answer": ""}
            )
            return {"answer": out["answer"], "context": out["context"]}
        ctx = _retrieve({"query": query, "top_k": top_k, "context": [], "answer": ""})[
            "context"
        ]
        ans = _generate(
            {"query": query, "top_k": top_k, "context": ctx, "answer": ""}
        )["answer"]
        return {"answer": ans, "context": ctx}

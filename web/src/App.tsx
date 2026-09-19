import { useState } from "react";
import { chat } from "./api";

export default function App() {
  const [input, setInput] = useState("");
  const [answer, setAnswer] = useState("");
  const [ctx, setCtx] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  async function send() {
    if (!input.trim() || busy) return;
    setBusy(true);
    setErr("");
    setAnswer("");
    setCtx([]);
    try {
      const res = await chat(input.trim());
      setAnswer(res.answer);
      setCtx(res.context);
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app">
      <header className="topbar">
        <span className="logo" aria-hidden="true">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 6h16M4 12h10M4 18h7" />
          </svg>
        </span>
        <h1 className="title">晨星 AI Stack · 调试台</h1>
      </header>

      <main className="panel">
        <section className="answer" aria-live="polite">
          {busy && <p className="muted">推理中…</p>}
          {err && <p className="error">{err}</p>}
          {answer && <p className="answer-text">{answer}</p>}
          {ctx.length > 0 && (
            <div className="ctx">
              <h2 className="ctx-title">召回上下文 ({ctx.length})</h2>
              <ul>
                {ctx.map((c, i) => (
                  <li key={i} className="ctx-item">
                    {c}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      </main>

      <footer className="composer">
        <input
          className="composer-input"
          value={input}
          placeholder="输入问题，回车发送…"
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") send();
          }}
        />
        <button className="composer-send" onClick={send} disabled={busy} aria-label="发送">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 2 11 13M22 2 15 22 11 13 2 9z" />
          </svg>
        </button>
      </footer>
    </div>
  );
}

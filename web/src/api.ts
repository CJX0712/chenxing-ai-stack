export interface ChatResp {
  answer: string;
  context: string[];
  model: string;
}

export async function chat(query: string, top_k = 3): Promise<ChatResp> {
  const r = await fetch("/v1/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k }),
  });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

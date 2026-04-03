const QUERY_API = "http://localhost:8001";
const WS_URL = "ws://localhost:8001/ws/anomalies";

export async function fetchLogs({ service = "", level = "", limit = 50 } = {}) {
  const params = new URLSearchParams();
  if (service) params.append("service", service);
  if (level) params.append("level", level);
  params.append("limit", limit);
  const res = await fetch(`${QUERY_API}/logs?${params}`);
  const data = await res.json();
  return data.logs;
}

export function connectAnomalySocket(onMessage) {
  const ws = new WebSocket(WS_URL);
  ws.onmessage = (e) => onMessage(JSON.parse(e.data));
  ws.onerror = (e) => console.error("WebSocket error", e);
  return ws;
}

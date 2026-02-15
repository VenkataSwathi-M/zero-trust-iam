// src/services/trustSocket.js
export function connectTrustSocket(onMessage, onError) {
  const token = localStorage.getItem("token");
  if (!token) throw new Error("Missing token");

  const wsBase = import.meta.env.VITE_WS_BASE_URL || "ws://192.168.31.211:8000";
  const url = `${wsBase}/ws/trust?token=${encodeURIComponent(token)}`;

  const ws = new WebSocket(url);

  ws.onopen = () => {
    // optional: request fresh snapshot
    ws.send("SNAPSHOT");
  };

  ws.onmessage = (ev) => {
    try {
      const data = JSON.parse(ev.data);
      onMessage?.(data);
    } catch {
      // ignore non-json
    }
  };

  ws.onerror = (e) => onError?.(e);
  ws.onclose = () => {};

  return ws;
}
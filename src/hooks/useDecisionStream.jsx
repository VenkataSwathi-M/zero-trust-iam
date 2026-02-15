import { useEffect, useRef, useState } from "react";

export default function useDecisionStream() {
  const [events, setEvents] = useState([]);
  const [trustMap, setTrustMap] = useState({});
  const wsRef = useRef(null);

  useEffect(() => {
    const host = window.location.hostname;
    const wsUrl = `ws://${host}:8000/ws/decisions`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data);

        setEvents((prev) => [msg, ...prev].slice(0, 200));

        if (
          msg?.event === "ACCESS_DECISION" &&
          msg.agent_id &&
          msg.trust !== undefined
        ) {
          setTrustMap((prev) => ({ ...prev, [msg.agent_id]: msg.trust }));
        }
      } catch {
        // ignore invalid JSON
      }
    };

    ws.onerror = () => {};
    return () => {
      try {
        ws.close();
      } catch {}
    };
  }, []);

  return { events, trustMap };
}
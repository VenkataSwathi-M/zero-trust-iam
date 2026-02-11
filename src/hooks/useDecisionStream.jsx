import { useEffect, useState } from "react";

export default function useDecisionStream() {
const [events, setEvents] = useState([]);
  const [trustMap, setTrustMap] = useState({}); // agent_id -> trust

useEffect(() => {
    const ws = new WebSocket("ws://127.0.0.1:8000/ws/decisions");

    ws.onmessage = (e) => {
    const data = JSON.parse(e.data);

    setEvents((prev) => [data, ...prev].slice(0, 300));

    if (data.event === "TRUST_UPDATE") {
        setTrustMap((prev) => ({ ...prev, [data.agent_id]: data.trust }));
    }
    };

    return () => ws.close();
}, []);

return { events, trustMap };
}
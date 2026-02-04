import { useEffect, useState } from "react";

export default function useDecisionStream() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/decisions");

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      // Keep only latest 50 events (prevents memory leak)
      setEvents((prev) => [data, ...prev].slice(0, 50));
    };

    ws.onerror = (err) => {
      console.error("WebSocket error", err);
    };

    return () => ws.close();
  }, []);

  return events;
}
// src/hooks/useTrustStream.js
import { useEffect, useRef, useState } from "react";
import { connectTrustSocket } from "../services/trustSocket";

export default function useTrustStream() {
  const [trust, setTrust] = useState(null);
  const [status, setStatus] = useState("connecting"); // connecting | open | closed
  const wsRef = useRef(null);

  useEffect(() => {
    let alive = true;

    try {
      const ws = connectTrustSocket(
        (msg) => {
          if (!alive) return;

          if (msg?.type === "TRUST") setTrust(msg);
          if (msg?.type === "ERROR") {
            setStatus("closed");
          }
        },
        () => {
          if (!alive) return;
          setStatus("closed");
        }
      );

      wsRef.current = ws;
      setStatus("open");
    } catch {
      setStatus("closed");
    }

    return () => {
      alive = false;
      try {
        wsRef.current?.close();
      } catch {}
    };
  }, []);

  return { trust, status };
}
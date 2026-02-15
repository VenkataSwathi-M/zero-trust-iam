// src/services/agentApi.js
import axios from "axios";

/**
 * Works automatically for:
 *  - http://localhost:3001        -> http://localhost:8000
 *  - http://192.168.31.211:3001   -> http://192.168.31.211:8000
 */
const host = window.location.hostname;

// If you set VITE_API_BASE_URL in .env, it will override.
// Example: VITE_API_BASE_URL=http://192.168.31.211:8000
const BASE_URL =
  import.meta.env.VITE_API_BASE_URL || `http://${host}:8000`;

const agentApi = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
});

// Attach agent JWT automatically (after OTP verify)
agentApi.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

agentApi.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err?.response?.status === 401) localStorage.removeItem("token");
    return Promise.reject(err);
  }
);

export default agentApi;

/* ======================
   DEVICE FINGERPRINT (SIM)
====================== */
export const generateDeviceFingerprint = () =>
  btoa(
    [
      navigator.userAgent,
      navigator.language,
      screen.width,
      screen.height,
      navigator.platform,
    ].join("|")
  );

/* ======================
   AUTH (Agent + OTP)
====================== */
// NOTE: Your backend currently uses /agent/auth/send-otp with agent_id+password
// so keep using your AgentLogin.jsx flow (send-otp -> returns sid -> verify-otp)

export const sendOtpWithPassword = async (agent_id, password) => {
  const res = await agentApi.post("/agent/auth/send-otp", { agent_id, password });
  return res.data; // {sid, ttl_minutes, message}
};

export const verifyOtp = async (sid, otp) => {
  const res = await agentApi.post("/agent/auth/verify-otp", { sid, otp });
  if (res.data?.access_token) localStorage.setItem("token", res.data.access_token);
  return res.data;
};

/* ======================
   ZERO TRUST ACCESS
====================== */
export const requestAccess = async (resource, action, metadata = {}) => {
  const res = await agentApi.post("/agentic-decision", { resource, action, metadata });
  return res.data;
};

/* ======================
   WEBSOCKET DECISIONS
====================== */
export const connectDecisionSocket = (onMessage) => {
  // Use ws/wss based on page protocol
  const wsProto = window.location.protocol === "https:" ? "wss" : "ws";
  const wsUrl = `${wsProto}://${host}:8000/ws/decisions`;

  const socket = new WebSocket(wsUrl);

  socket.onmessage = (event) => {
    try {
      onMessage?.(JSON.parse(event.data));
    } catch (e) {
      console.error("WS parse error:", e);
    }
  };

  socket.onerror = (err) => console.error("WebSocket error:", err);
  socket.onclose = () => console.warn("WebSocket closed");

  return socket;
};

/* ======================
   WEBSOCKET TRUST (for live trust score)
====================== */
export const connectTrustSocket = (sid, onMessage) => {
  const wsProto = window.location.protocol === "https:" ? "wss" : "ws";
  const wsUrl = `${wsProto}://${host}:8000/ws/trust?sid=${encodeURIComponent(sid)}`;

  const socket = new WebSocket(wsUrl);

  socket.onmessage = (event) => {
    try {
      onMessage?.(JSON.parse(event.data));
    } catch (e) {
      console.error("WS parse error:", e);
    }
  };

  socket.onerror = (err) => console.error("Trust WS error:", err);
  socket.onclose = () => console.warn("Trust WS closed");

  return socket;
};
// src/services/adminApi.js
import axios from "axios";

// Works for localhost + LAN IP automatically
const host = window.location.hostname; // "localhost" or "192.168.31.211"
const BASE_URL = "http://192.168.31.211:8000";

const adminApi = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
});

// Attach admin token on every request
adminApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("admin_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

// Auto-handle 401
adminApi.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err?.response?.status === 401) {
      localStorage.removeItem("admin_token");
      // optional redirect:
      // window.location.href = "/admin/login";
    }
    return Promise.reject(err);
  }
);

export default adminApi;

/* =======================
   AGENTS
======================= */
export const createAgent = async (data) => {
  const res = await adminApi.post("/admin/agents", data);
  return res.data;
};

export const getAgents = async () => {
  const res = await adminApi.get("/admin/agents");
  return res.data;
};

/* =======================
   POLICIES
======================= */
export const createPolicy = async (data) => {
  const res = await adminApi.post("/admin/policies", data);
  return res.data;
};

export const getPolicies = async () => {
  const res = await adminApi.get("/admin/policies");
  return res.data;
};

export const togglePolicyActive = async (policyId, active) => {
  const res = await adminApi.patch(`/admin/policies/${policyId}`, { active });
  return res.data;
};

/* =======================
   AUDIT LOGS
======================= */
export const getAuditLogs = async ({ agent_id, limit = 50 } = {}) => {
  const params = {};
  if (agent_id) params.agent_id = agent_id;
  params.limit = limit;

  const res = await adminApi.get("/admin/audit/logs", { params });
  return res.data;
};

/* =======================
   METRICS (trust + risk)
======================= */
export const getOverview = async () => {
  const res = await adminApi.get("/admin/metrics/overview");
  return res.data;
};

export const getRiskHistory = async (agentId) => {
  const res = await adminApi.get(`/admin/metrics/risk-history/${agentId}`);
  return res.data;
};

export const getTrustHistory = async (agentId, limit = 60) => {
  const res = await adminApi.get(`/admin/metrics/trust-history/${agentId}`, {
    params: { limit },
  });
  return res.data;
};
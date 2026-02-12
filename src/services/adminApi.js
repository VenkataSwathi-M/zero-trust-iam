// src/services/adminApi.js
import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// ✅ Attach Admin token automatically on every request
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("admin_token"); // ✅ must match what you store
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

const adminApi = {
  get: (url, config) => API.get(url, config),
  post: (url, data, config) => API.post(url, data, config),
  put: (url, data, config) => API.put(url, data, config),
  patch: (url, data, config) => API.patch(url, data, config), // ✅ add patch
  delete: (url, config) => API.delete(url, config),
};

export default adminApi;

/* =======================
AGENTS
======================= */
export const createAgent = async (data) => {
  const res = await API.post("/admin/agents", data);
  return res.data;
};

export const getAgents = async () => {
  const res = await API.get("/admin/agents");
  return res.data;
};

/* =======================
POLICIES
======================= */
export const createPolicy = async (data) => {
  const res = await API.post("/admin/policies", data); // ✅ was api (wrong)
  return res.data;
};

export const getPolicies = async () => {
  const res = await API.get("/admin/policies"); // ✅ was api (wrong)
  return res.data;
};

export const togglePolicyActive = async (policyId, active) => {
  const res = await API.patch(`/admin/policies/${policyId}`, { active }); // ✅ was api (wrong)
  return res.data;
};
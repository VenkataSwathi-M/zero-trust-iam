import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// ✅ Default export object (so Dashboard can do adminApi.get/post)
const adminApi = {
  get: (url, config) => API.get(url, config),
  post: (url, data, config) => API.post(url, data, config),
  put: (url, data, config) => API.put(url, data, config),
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
  const res = await API.post("/admin/policies", data);
  return res.data;
};

export const getPolicies = async () => {
  const res = await API.get("/admin/policies");
  return res.data;
};
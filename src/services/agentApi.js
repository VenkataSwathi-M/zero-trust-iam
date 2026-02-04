import api from "./api";

export const agentLogin = async (payload) => {
  const res = await api.post("/api/agent/login", payload);
  return res.data;
};
import api from "./api"; // your axios instance that adds token interceptor

export const requestAccess = async (resource, action, metadata = {}) => {
  const token = localStorage.getItem("token");

  if (!token) {
    throw new Error("No token found. Please login again.");
  }

  const res = await api.post(
    "/agentic-decision",
    {
      resource,
      action,
      metadata,
    },
    {
      headers: {
        Authorization: `Bearer ${token}`, // ✅ force attach
      },
    }
  );

  return res.data;
};
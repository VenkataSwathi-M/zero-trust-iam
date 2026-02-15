// src/services/api.js
import axios from "axios";

const baseURL =
  import.meta.env.VITE_API_BASE_URL || `http://${window.location.hostname}:8000`;

const api = axios.create({
  baseURL,
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err?.response?.status === 401) localStorage.removeItem("token");
    return Promise.reject(err);
  }
);

export default api;
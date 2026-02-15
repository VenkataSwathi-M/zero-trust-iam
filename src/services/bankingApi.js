import axios from "axios";

const BASE_URL = "http://192.168.31.211:8000";

const bankingApi = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
});

// attach token
bankingApi.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default bankingApi;

/* ------------------ READ ------------------ */

export const getMyAccount = async () =>
  (await bankingApi.get("/banking/me")).data;

export const getMyTransactions = async (limit = 50) =>
  (await bankingApi.get("/banking/transactions", { params: { limit } })).data;

export const getBeneficiaries = async () =>
  (await bankingApi.get("/banking/beneficiaries")).data;

/* ------------------ WRITE ------------------ */

export const updateProfile = async ({ name, phone }) =>
  (await bankingApi.post("/banking/profile", { name, phone })).data;

/* ------------------ TRANSFER ------------------ */

export const makeTransfer = async ({ to_account, amount, note }) =>
  (await bankingApi.post("/banking/transfer", {
    to_account,
    amount,
    note,
  })).data;
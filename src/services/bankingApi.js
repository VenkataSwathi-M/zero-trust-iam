import api from "./api";

export const listAccounts = async () => (await api.get("/banking/accounts")).data;

export const createAccount = async (payload) =>
  (await api.post("/banking/accounts", payload)).data;

export const updateAccount = async (id, payload) =>
  (await api.put(`/banking/accounts/${id}`, payload)).data;

export const transferMoney = async (payload) =>
  (await api.post("/banking/transfer", payload)).data;
import agentApi from "./agentApi";

export const getSessionMe = () =>
  agentApi.get("/session/me").then(r => r.data);
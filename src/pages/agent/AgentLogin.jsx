import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";
import { Box, Card, CardContent, TextField, Typography, Button, Alert } from "@mui/material";

export default function AgentLogin() {
  const navigate = useNavigate();

  const [agentId, setAgentId] = useState("");
  const [password, setPassword] = useState("");

  const [otp, setOtp] = useState("");
  const [decisionId, setDecisionId] = useState("");

  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

  const [err, setErr] = useState("");
  const [info, setInfo] = useState("");

  const sendOtp = async () => {
    try {
      setErr("");
      setInfo("");
      setLoading(true);

      const res = await api.post("/agent/auth/login", {
        agent_id: agentId,
        password,
      });

      const did = res?.data?.decision_id;
      if (!did) throw new Error("Backend did not return decision_id");

      setDecisionId(did);
      setStep(2);
      setInfo("OTP sent. Check email / backend console (DEV OTP).");
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || "Unknown error";
      setErr(msg);
    } finally {
      setLoading(false);
    }
  };

  const verifyOtp = async () => {
    try {
      setErr("");
      setInfo("");
      setLoading(true);

      const res = await api.post("/agent/auth/verify-otp", {
        agent_id: agentId,
        otp,
        decision_id: decisionId,
      });

      const token = res?.data?.access_token;
      if (!token) throw new Error("Backend did not return access_token");

      localStorage.setItem("token", token);
      setInfo("Login successful. Redirecting...");
      navigate("/agent/dashboard");
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || "Unknown error";
      setErr(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: "70vh", display: "flex", justifyContent: "center", alignItems: "center" }}>
      <Card sx={{ width: 420, borderRadius: 3 }}>
        <CardContent>
          <Typography variant="h6" fontWeight="bold">Agent Login</Typography>

          {err && <Alert severity="error" sx={{ mt: 2 }}>{String(err)}</Alert>}
          {info && <Alert severity="success" sx={{ mt: 2 }}>{String(info)}</Alert>}

          {step === 1 && (
            <>
              <TextField
                fullWidth sx={{ mt: 2 }}
                label="Agent ID"
                value={agentId}
                onChange={(e) => setAgentId(e.target.value)}
              />
              <TextField
                fullWidth sx={{ mt: 2 }}
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <Button
                fullWidth sx={{ mt: 3 }}
                variant="contained"
                onClick={sendOtp}
                disabled={loading || !agentId || !password}
              >
                {loading ? "Sending…" : "Send OTP"}
              </Button>
            </>
          )}

          {step === 2 && (
            <>
              <TextField
                fullWidth sx={{ mt: 2 }}
                label="Enter OTP"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
              />
              <Button
                fullWidth sx={{ mt: 3 }}
                variant="contained"
                onClick={verifyOtp}
                disabled={loading || !otp || !decisionId}
              >
                {loading ? "Verifying…" : "Verify OTP"}
              </Button>
              <Button
                fullWidth sx={{ mt: 1 }}
                variant="text"
                onClick={() => {
                  setStep(1);
                  setOtp("");
                  setDecisionId("");
                  setErr("");
                  setInfo("");
                }}
              >
                Back
              </Button>
            </>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
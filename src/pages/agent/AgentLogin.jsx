// src/pages/agent/AgentLogin.jsx
import { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import agentApi from "../../services/agentApi";

export default function AgentLogin() {
  const navigate = useNavigate();

  const [agentId, setAgentId] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [sid, setSid] = useState(""); // ✅ store session id from send-otp

  const [step, setStep] = useState(1); // 1 = send otp, 2 = verify otp
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");

  const safeError = (e, fallback) =>
    e?.response?.data?.detail ||
    e?.response?.data?.message ||
    e?.message ||
    fallback;

  const handleSendOtp = async () => {
    setErr("");
    setMsg("");

    if (!agentId.trim() || !password) {
      setErr("Agent ID and password required");
      return;
    }

    try {
      setLoading(true);

      const res = await agentApi.post("/agent/auth/send-otp", {
        agent_id: agentId.trim(),
        password,
      });

      // ✅ backend returns sid
      const newSid = res?.data?.sid;
      if (!newSid) throw new Error("sid not received from backend");

      setSid(newSid);

      // If OTP_MODE=DEV your API may return otp too (optional)
      if (res?.data?.otp) {
        setMsg(`OTP generated (DEV): ${res.data.otp}`);
      } else {
        setMsg("OTP sent to registered email ✅");
      }

      setStep(2);
    } catch (e) {
      setErr(safeError(e, "Failed to send OTP"));
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async () => {
    setErr("");
    setMsg("");

    if (!sid) {
      setErr("sid missing. Please click SEND OTP again.");
      setStep(1);
      return;
    }

    if (!otp.trim()) {
      setErr("OTP required");
      return;
    }

    try {
      setLoading(true);

      // ✅ verify endpoint expects { sid, otp }
      const res = await agentApi.post("/agent/auth/verify-otp", {
        sid,
        otp: otp.trim(),
      });

      const token = res?.data?.access_token;
      if (!token) throw new Error("Token not received");

      localStorage.setItem("token", token);
      localStorage.setItem("agent_id", agentId.trim());

      setMsg("Login success ✅ Redirecting...");
      navigate("/agent/dashboard");
    } catch (e) {
      setErr(safeError(e, "OTP verification failed"));
    } finally {
      setLoading(false);
    }
  };

  const resetAll = () => {
    setStep(1);
    setOtp("");
    setSid("");
    setMsg("");
    setErr("");
  };

  return (
    <Box sx={{ display: "flex", justifyContent: "center", mt: 10 }}>
      <Card sx={{ width: 420 }}>
        <CardContent>
          <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>
            Agent Login (OTP)
          </Typography>

          {err && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {String(err)}
            </Alert>
          )}
          {msg && (
            <Alert severity="success" sx={{ mb: 2 }}>
              {String(msg)}
            </Alert>
          )}

          <TextField
            fullWidth
            label="Agent ID"
            value={agentId}
            onChange={(e) => setAgentId(e.target.value)}
            sx={{ mb: 2 }}
            disabled={loading || step === 2}
            placeholder="Agent_01"
          />

          <TextField
            fullWidth
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            sx={{ mb: 2 }}
            disabled={loading || step === 2}
          />

          {step === 2 && (
            <>
              <TextField
                fullWidth
                label="OTP"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                sx={{ mb: 2 }}
                disabled={loading}
                placeholder="6-digit OTP"
              />

              {/* helpful debug: show sid (optional) */}
              <Typography variant="caption" sx={{ display: "block", mb: 2, opacity: 0.7 }}>
                sid: {sid}
              </Typography>
            </>
          )}

          {step === 1 ? (
            <Button
              fullWidth
              variant="contained"
              onClick={handleSendOtp}
              disabled={loading}
            >
              {loading ? "Sending..." : "SEND OTP"}
            </Button>
          ) : (
            <Box sx={{ display: "flex", gap: 1 }}>
              <Button
                fullWidth
                variant="contained"
                onClick={handleVerifyOtp}
                disabled={loading}
              >
                {loading ? "Verifying..." : "VERIFY OTP"}
              </Button>

              <Button variant="outlined" onClick={resetAll} disabled={loading}>
                Back
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
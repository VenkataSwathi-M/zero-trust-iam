import { useEffect, useMemo, useRef, useState } from "react";
import { jwtDecode } from "jwt-decode";
import api from "../../services/api";
import {
  Box,
  Button,
  Typography,
  TextField,
  Paper,
  Chip,
  Stack,
  LinearProgress,
  Alert,
  Divider,
} from "@mui/material";

export default function AgentDashboard() {
  const token = localStorage.getItem("token");

  // ---- Guard ----
  const decoded = useMemo(() => {
    try {
      return token ? jwtDecode(token) : null;
    } catch {
      return null;
    }
  }, [token]);

  const agentId = decoded?.sub || "—";

  // ✅ Trust should be STATE (not constant from JWT)
  const [trust, setTrust] = useState(() => {
    const initial = Number(decoded?.trust ?? 0);
    return Number.isFinite(initial) ? initial : 0;
  });

  const [maxAccess, setMaxAccess] = useState(decoded?.max_access || "read");
  const [stepUpRequired, setStepUpRequired] = useState(false);

  // WS status
  const [wsStatus, setWsStatus] = useState("connecting"); // connecting | live | offline
  const wsRef = useRef(null);

  // MFA UI
  const [showMfa, setShowMfa] = useState(false);
  const [otp, setOtp] = useState("");
  const [status, setStatus] = useState("");
  const [decisionId, setDecisionId] = useState("");
  const [loading, setLoading] = useState(false);

  // ---------------- WebSocket Trust Stream ----------------
  useEffect(() => {
    if (!token) {
      setWsStatus("offline");
      return;
    }

    const wsBase = import.meta.env.VITE_WS_BASE_URL || "ws://192.168.31.211:8000";
    const url = `${wsBase}/ws/trust?token=${encodeURIComponent(token)}`;

    setWsStatus("connecting");

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setWsStatus("live");
      // ask for immediate snapshot
      try {
        ws.send("SNAPSHOT");
      } catch {}
    };

    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);

        if (msg?.type === "TRUST") {
          // backend sends effective_trust 0..1
          const t = Number(msg.effective_trust);
          if (Number.isFinite(t)) setTrust(t);

          if (msg.max_access) setMaxAccess(msg.max_access);
          setStepUpRequired(Boolean(msg.step_up));
        }

        if (msg?.type === "ERROR") {
          setWsStatus("offline");
        }
      } catch {
        // ignore non-json
      }
    };

    ws.onerror = () => setWsStatus("offline");
    ws.onclose = () => setWsStatus("offline");

    return () => {
      try {
        ws.close();
      } catch {}
    };
  }, [token]);

  const trustPct = Math.round(Math.max(0, Math.min(1, trust)) * 100);

  // ---------------- Secure Action ----------------
  const handleAction = async () => {
    try {
      setLoading(true);
      setStatus("");

      const res = await api.post("/agentic-decision", {
        action: "transfer",
        resource: "banking/account/123",
      });

      if (res.data.decision === "STEP_UP") {
        setDecisionId(res.data.decision_id);

        // request OTP
        await api.post("/mfa/request", {
          decision_id: res.data.decision_id,
        });

        setShowMfa(true);
        setStatus("Additional verification required (MFA)");
      } else if (res.data.decision === "ALLOW") {
        setStatus("Access granted ✅");
      } else {
        setStatus("Access denied ❌");
      }
    } catch (err) {
      setStatus(err.response?.data?.detail || "Error occurred");
    } finally {
      setLoading(false);
    }
  };

  // ---------------- Verify MFA ----------------
  const verifyMfa = async () => {
    try {
      setLoading(true);

      const res = await api.post("/mfa/verify", {
        decision_id: decisionId,
        otp: otp,
      });

      if (res.data.status === "VERIFIED") {
        setStatus("MFA verified ✅ Access granted");
        setShowMfa(false);
        setOtp("");
      }
    } catch {
      setStatus("Invalid or expired OTP ❌");
    } finally {
      setLoading(false);
    }
  };

  if (!token || !decoded) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="warning">Token missing/invalid. Please login again.</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Typography variant="h4" fontWeight={900}>
          Agent Dashboard
        </Typography>

        <Chip
          size="small"
          color={wsStatus === "live" ? "success" : wsStatus === "connecting" ? "warning" : "default"}
          label={wsStatus === "live" ? "LIVE" : wsStatus === "connecting" ? "CONNECTING" : "OFFLINE"}
        />
      </Stack>

      {/* Trust Info */}
      <Paper sx={{ p: 2, mb: 2, borderRadius: 3 }}>
        <Stack direction={{ xs: "column", sm: "row" }} spacing={2} alignItems="center">
          <Box sx={{ flex: 1 }}>
            <Typography>
              <strong>Agent ID:</strong> {agentId}
            </Typography>

            <Typography sx={{ mt: 0.5 }}>
              <strong>Trust (Live):</strong> {trustPct}%
            </Typography>

            <LinearProgress sx={{ mt: 1, borderRadius: 1 }} variant="determinate" value={trustPct} />

            <Stack direction="row" spacing={1} sx={{ mt: 1, flexWrap: "wrap" }}>
              <Chip size="small" label={`Max Access: ${maxAccess}`} />
              <Chip
                size="small"
                color={stepUpRequired ? "warning" : "success"}
                label={stepUpRequired ? "Step-up Required" : "Step-up OK"}
              />
            </Stack>
          </Box>

          <Divider orientation="vertical" flexItem sx={{ display: { xs: "none", sm: "block" } }} />

          <Box>
            <Typography variant="body2" sx={{ opacity: 0.7 }}>
              Tip: Trust updates automatically when backend bumps trust or applies decay.
            </Typography>
          </Box>
        </Stack>
      </Paper>

      {/* Step-up alert (from WS or backend) */}
      {stepUpRequired && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Your session needs step-up verification (fingerprint/OTP) to continue high-risk actions.
        </Alert>
      )}

      {/* Secure Action */}
      <Button variant="contained" onClick={handleAction} disabled={loading} sx={{ borderRadius: 2 }}>
        {loading ? "Processing..." : "Perform Secure Action"}
      </Button>

      {/* MFA Section */}
      {showMfa && (
        <Paper sx={{ p: 2, mt: 3, borderRadius: 3 }}>
          <Typography gutterBottom fontWeight={800}>
            Enter OTP for Step-Up Verification
          </Typography>

          <TextField
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            placeholder="6-digit OTP"
            fullWidth
            sx={{ mb: 2 }}
          />

          <Button variant="contained" onClick={verifyMfa} disabled={!otp || loading}>
            Verify OTP
          </Button>
        </Paper>
      )}

      {/* Status */}
      {status && (
        <Typography sx={{ mt: 3, fontWeight: 700 }}>
          {status}
        </Typography>
      )}
    </Box>
  );
}
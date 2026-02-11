import { useState } from "react";
import { jwtDecode } from "jwt-decode";
import api from "../../services/api";
import {
  Box,
  Button,
  Typography,
  TextField,
  Paper
} from "@mui/material";

export default function AgentDashboard() {
  const token = localStorage.getItem("token");

  // 🔐 Decode JWT to get agent_id + trust score
  const decoded = jwtDecode(token);
  const agentId = decoded.sub;
  const trustScore = decoded.trust;

  const [showMfa, setShowMfa] = useState(false);
  const [otp, setOtp] = useState("");
  const [status, setStatus] = useState("");
  const [decisionId, setDecisionId] = useState("");
  const [loading, setLoading] = useState(false);

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

        // 🔐 MFA request (agent_id comes from JWT in backend)
        await api.post("/mfa/request", {
          decision_id: res.data.decision_id,
        });

        setShowMfa(true);
        setStatus("Additional verification required (MFA)");
      } 
      else if (res.data.decision === "ALLOW") {
        setStatus("Access granted ✅");
      } 
      else {
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

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Agent Dashboard
      </Typography>

      {/* Trust Info */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography>
          <strong>Agent ID:</strong> {agentId}
        </Typography>
        <Typography>
          <strong>Trust Score:</strong> {trustScore}
        </Typography>
      </Paper>

      {/* Secure Action */}
      <Button
        variant="contained"
        onClick={handleAction}
        disabled={loading}
      >
        {loading ? "Processing..." : "Perform Secure Action"}
      </Button>

      {/* MFA Section */}
      {showMfa && (
        <Paper sx={{ p: 2, mt: 3 }}>
          <Typography gutterBottom>
            Enter OTP for Step-Up Verification
          </Typography>

          <TextField
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            placeholder="6-digit OTP"
            fullWidth
            sx={{ mb: 2 }}
          />

          <Button
            variant="contained"
            onClick={verifyMfa}
            disabled={!otp || loading}
          >
            Verify OTP
          </Button>
        </Paper>
      )}

      {/* Status */}
      {status && (
        <Typography sx={{ mt: 3 }}>
          {status}
        </Typography>
      )}
    </Box>
  );
}
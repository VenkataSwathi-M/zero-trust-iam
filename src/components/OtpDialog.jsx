import { useState } from "react";
import { Dialog, DialogTitle, DialogContent, TextField, Button, Alert } from "@mui/material";
import { verifyOtp } from "../services/agentApi";

export default function OtpDialog({ open, agentId, onClose, onVerified }) {
  const [otp, setOtp] = useState("");
  const [err, setErr] = useState("");

  const handleVerify = async () => {
    try {
      setErr("");
      await verifyOtp(agentId, otp);
      onVerified();
      onClose();
    } catch (e) {
      setErr(e?.response?.data?.detail || e?.message || "OTP verify failed");
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="xs">
      <DialogTitle>OTP Verification (STEP_UP)</DialogTitle>
      <DialogContent>
        {err && <Alert severity="error" sx={{ mb: 1 }}>{err}</Alert>}

        <TextField
          label="Enter OTP"
          value={otp}
          onChange={(e) => setOtp(e.target.value)}
          fullWidth
          sx={{ mt: 1 }}
        />

        <Button variant="contained" fullWidth sx={{ mt: 2 }} onClick={handleVerify}>
          Verify OTP
        </Button>
      </DialogContent>
    </Dialog>
  );
}
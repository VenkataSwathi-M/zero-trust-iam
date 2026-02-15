import { useEffect, useMemo, useState } from "react";
import {
  Box, Card, CardContent, Typography, TextField, Button, Alert, Chip,
  Stack, Divider, Dialog, DialogTitle, DialogContent, DialogActions,
  LinearProgress, Tooltip
} from "@mui/material";
import FingerprintIcon from "@mui/icons-material/Fingerprint";
import SecurityIcon from "@mui/icons-material/Security";
import SwapHorizIcon from "@mui/icons-material/SwapHoriz";
import agentApi from "../../services/agentApi";

const STEP_UP_AMOUNT = 25000;

function formatINR(n) {
  if (n === null || n === undefined) return "₹0.00";
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(Number(n));
}

export default function BankingTransfer() {
  const [toAccount, setToAccount] = useState("");
  const [amount, setAmount] = useState("");
  const [note, setNote] = useState("");

  const [me, setMe] = useState(null);
  const [trust, setTrust] = useState(0.85);
  const [loadingMe, setLoadingMe] = useState(true);

  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [msg, setMsg] = useState("");

  // step-up modal
  const [stepUpOpen, setStepUpOpen] = useState(false);
  const [fingerprintBusy, setFingerprintBusy] = useState(false);
  const [fingerprintOk, setFingerprintOk] = useState(false);

  const parsedAmount = useMemo(() => {
    const x = Number(amount);
    return Number.isFinite(x) ? x : 0;
  }, [amount]);

  const needsStepUp = parsedAmount >= STEP_UP_AMOUNT;

  // Load account summary (logged-in agent)
  useEffect(() => {
    (async () => {
      try {
        setLoadingMe(true);
        setErr("");
        const res = await agentApi.get("/banking/me");
        setMe(res.data);
      } catch (e) {
        setErr(e?.response?.data?.detail || "Account not found / API error");
      } finally {
        setLoadingMe(false);
      }
    })();
  }, []);

  // Open step-up automatically when amount crosses threshold
  useEffect(() => {
    if (needsStepUp && parsedAmount > 0) {
      setFingerprintOk(false);
      setStepUpOpen(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [needsStepUp]);

  const runFingerprint = async () => {
    setFingerprintBusy(true);
    setFingerprintOk(false);
    // Fake “scan” feel
    await new Promise((r) => setTimeout(r, 1200));
    setFingerprintOk(true);
    setFingerprintBusy(false);
  };

  const handleTransfer = async () => {
    setErr("");
    setMsg("");

    if (!toAccount || !amount) {
      setErr("To Account and Amount required");
      return;
    }

    if (parsedAmount <= 0) {
      setErr("Amount must be greater than 0");
      return;
    }

    // If step-up required, block transfer until fingerprint ok
    if (needsStepUp && !fingerprintOk) {
      setStepUpOpen(true);
      setErr("Step-up required: verify fingerprint to proceed.");
      return;
    }

    try {
      setLoading(true);

      const res = await agentApi.post("/banking/transfer", {
        to_account: toAccount,
        amount: parsedAmount,
        note,
        step_up: needsStepUp ? "FINGERPRINT" : "NONE",
      });

      setMsg(res?.data?.message || "Transfer success ✅");
      setToAccount("");
      setAmount("");
      setNote("");
      setFingerprintOk(false);

      // refresh balance after transfer
      const me2 = await agentApi.get("/banking/me");
      setMe(me2.data);
    } catch (e) {
      setErr(e?.response?.data?.detail || "Transfer failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: "auto", p: 3 }}>
      <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems="stretch">
        {/* LEFT: Zero Trust + Account */}
        <Box sx={{ width: { xs: "100%", md: 360 } }}>
          <Card sx={{ borderRadius: 3, boxShadow: 2 }}>
            <CardContent>
              <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between">
                <Typography fontWeight={800}>Zero-Trust Status</Typography>
                <Chip icon={<SecurityIcon />} label="Protected" size="small" />
              </Stack>

              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" sx={{ opacity: 0.75 }}>Trust Score</Typography>
                <Typography variant="h4" fontWeight={900}>
                  {Math.round(trust * 100)}%
                </Typography>
                <LinearProgress variant="determinate" value={trust * 100} sx={{ mt: 1, height: 8, borderRadius: 999 }} />
              </Box>

              <Stack direction="row" spacing={1} sx={{ mt: 2, flexWrap: "wrap" }}>
                <Chip label="Access: transfer" size="small" />
                <Chip
                  color={needsStepUp ? "warning" : "success"}
                  icon={<FingerprintIcon />}
                  label={needsStepUp ? "Step-up: Required" : "Step-up: Not needed"}
                  size="small"
                />
              </Stack>

              <Divider sx={{ my: 2 }} />

              <Typography variant="body2" sx={{ opacity: 0.75 }}>
                Account Balance
              </Typography>

              {loadingMe ? (
                <Typography sx={{ mt: 1 }}>Loading...</Typography>
              ) : (
                <Typography variant="h5" fontWeight={900} sx={{ mt: 0.5 }}>
                  {formatINR(me?.balance || 0)}
                </Typography>
              )}

              <Typography variant="caption" sx={{ opacity: 0.7 }}>
                IFSC: {me?.ifsc || "-"} • A/C: {me?.account_no || "-"}
              </Typography>
            </CardContent>
          </Card>
        </Box>

        {/* RIGHT: Transfer Form */}
        <Box sx={{ flex: 1 }}>
          <Card sx={{ borderRadius: 3, boxShadow: 2 }}>
            <CardContent>
              <Stack direction="row" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h5" fontWeight={900}>Fund Transfer</Typography>
                  <Typography variant="body2" sx={{ opacity: 0.75 }}>
                    Add beneficiary account and transfer securely.
                  </Typography>
                </Box>

                <Chip icon={<SwapHorizIcon />} label="IMPS/NEFT" />
              </Stack>

              <Divider sx={{ my: 2 }} />

              {err && <Alert severity="error" sx={{ mb: 2 }}>{err}</Alert>}
              {msg && <Alert severity="success" sx={{ mb: 2 }}>{msg}</Alert>}

              <Stack spacing={2}>
                <TextField
                  label="Beneficiary Account Number"
                  value={toAccount}
                  onChange={(e) => setToAccount(e.target.value)}
                  placeholder="e.g. 999000111222"
                  fullWidth
                />

                <TextField
                  label="Amount (INR)"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="e.g. 2000"
                  fullWidth
                />

                <TextField
                  label="Remarks (optional)"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  fullWidth
                />

                <Stack direction={{ xs: "column", sm: "row" }} spacing={1} alignItems="center">
                  <Button
                    variant="contained"
                    size="large"
                    onClick={handleTransfer}
                    disabled={loading}
                    sx={{ borderRadius: 2, px: 3 }}
                    fullWidth
                  >
                    {loading ? "Processing..." : "Transfer"}
                  </Button>

                  <Tooltip title={`Transfers ≥ ₹${STEP_UP_AMOUNT.toLocaleString("en-IN")} require fingerprint`}>
                    <Button
                      variant="outlined"
                      size="large"
                      startIcon={<FingerprintIcon />}
                      onClick={() => setStepUpOpen(true)}
                      sx={{ borderRadius: 2 }}
                      fullWidth
                    >
                      Step-up
                    </Button>
                  </Tooltip>
                </Stack>

                <Typography variant="caption" sx={{ opacity: 0.7 }}>
                  Note: High amounts trigger Step-up authentication (Fingerprint) as per Zero-Trust policy.
                </Typography>
              </Stack>
            </CardContent>
          </Card>
        </Box>
      </Stack>

      {/* Fingerprint Step-up Modal */}
      <Dialog open={stepUpOpen} onClose={() => setStepUpOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle sx={{ fontWeight: 900 }}>Fingerprint Verification</DialogTitle>
        <DialogContent>
          <Alert severity={fingerprintOk ? "success" : "info"} sx={{ mb: 2 }}>
            {fingerprintOk
              ? "Fingerprint verified ✅ You can proceed."
              : `Required for transfers ≥ ₹${STEP_UP_AMOUNT.toLocaleString("en-IN")}.`}
          </Alert>

          <Card sx={{ borderRadius: 3, boxShadow: 0, border: "1px solid #eee" }}>
            <CardContent>
              <Stack alignItems="center" spacing={1}>
                <FingerprintIcon sx={{ fontSize: 64 }} />
                <Typography fontWeight={800}>Touch sensor to verify</Typography>
                <Typography variant="caption" sx={{ opacity: 0.7 }}>
                  (Demo) This simulates biometric verification.
                </Typography>
              </Stack>
            </CardContent>
          </Card>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setStepUpOpen(false)} disabled={fingerprintBusy}>Close</Button>
          <Button variant="contained" onClick={runFingerprint} disabled={fingerprintBusy || fingerprintOk}>
            {fingerprintBusy ? "Scanning..." : fingerprintOk ? "Verified" : "Verify"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
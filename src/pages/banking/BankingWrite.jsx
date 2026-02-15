import { useState } from "react";
import { Box, Card, CardContent, Typography, TextField, Button, Alert, Stack } from "@mui/material";
import TrustBar from "../../components/TrustBar";
import { updateProfile } from "../../services/bankingApi";

export default function BankingWrite() {
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");

  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");

  const submit = async () => {
    setErr(""); setMsg("");
    try {
      setLoading(true);
      const res = await updateProfile({ name, phone });
      setMsg(res?.message || "Updated");
    } catch (e) {
      const d = e?.response?.data?.detail;
      setErr(d?.message || d || e.message || "Failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ px: 3, py: 2 }}>
      <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
        <Box sx={{ width: { xs: "100%", md: 360 } }}>
          <TrustBar />
        </Box>

        <Card sx={{ borderRadius: 3, flex: 1 }}>
          <CardContent>
            <Typography variant="h5" fontWeight={900} sx={{ mb: 1 }}>
              Banking (Write)
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.75, mb: 2 }}>
              Requires write access + higher trust.
            </Typography>

            {err && <Alert severity="error" sx={{ mb: 2 }}>{String(err)}</Alert>}
            {msg && <Alert severity="success" sx={{ mb: 2 }}>{String(msg)}</Alert>}

            <TextField fullWidth label="Full Name" value={name} onChange={(e) => setName(e.target.value)} sx={{ mb: 2 }} />
            <TextField fullWidth label="Phone" value={phone} onChange={(e) => setPhone(e.target.value)} sx={{ mb: 2 }} />

            <Button variant="contained" onClick={submit} disabled={loading}>
              {loading ? "Saving..." : "Save Profile"}
            </Button>
          </CardContent>
        </Card>
      </Stack>
    </Box>
  );
}
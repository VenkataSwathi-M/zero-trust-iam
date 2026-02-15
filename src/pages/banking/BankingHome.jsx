import { useEffect, useState } from "react";
import { Box, Card, CardContent, Typography, Button, Alert } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { getMyAccount } from "../../services/bankingApi";

export default function BankingHome() {
  const [acc, setAcc] = useState(null);
  const [err, setErr] = useState("");
  const nav = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        setErr("");
        const data = await getMyAccount();
        setAcc(data);
      } catch (e) {
        setErr(e?.response?.data?.detail || e?.message || "Failed to load account");
      }
    })();
  }, []);

  return (
    <Box sx={{ display: "grid", gap: 2 }}>
      {err && <Alert severity="error">{err}</Alert>}

      <Card>
        <CardContent>
          <Typography variant="h6" fontWeight="bold">Banking Overview</Typography>
          <Typography sx={{ mt: 1 }}>
            Account: <b>{acc?.account_no || "—"}</b> • IFSC: <b>{acc?.ifsc || "—"}</b>
          </Typography>

          <Typography variant="h4" sx={{ mt: 2 }}>
            ₹ {acc?.balance?.toFixed?.(2) ?? "—"}
          </Typography>
          <Typography color="text.secondary">Available Balance</Typography>

          <Box sx={{ display: "flex", gap: 2, mt: 2 }}>
            <Button variant="contained" onClick={() => nav("/banking/transfer")}>
              Transfer Money
            </Button>
            <Button variant="outlined" onClick={() => nav("/banking/transactions")}>
              View Transactions
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
import { useEffect, useMemo, useState } from "react";
import {
  Box, Card, CardContent, Typography, Chip, Divider, Button, Stack,
  Skeleton, Alert, Table, TableBody, TableCell, TableHead, TableRow, Paper
} from "@mui/material";
import Grid from "@mui/material/Grid";
import AccountBalanceWalletRoundedIcon from "@mui/icons-material/AccountBalanceWalletRounded";
import SwapHorizRoundedIcon from "@mui/icons-material/SwapHorizRounded";
import ReceiptLongRoundedIcon from "@mui/icons-material/ReceiptLongRounded";
import ShieldRoundedIcon from "@mui/icons-material/ShieldRounded";
import { useNavigate } from "react-router-dom";

import TrustBar from "../../components/TrustBar";
import { getMyAccount, getMyTransactions } from "../../services/bankingApi";
import { mockAccount, mockTransactions } from "../../mock/bankingData";

const money = (v, currency = "INR") =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency }).format(Number(v || 0));

export default function BankingRead() {
  const navigate = useNavigate();
  const useMock = import.meta.env.VITE_USE_MOCK_BANKING === "true";

  const [account, setAccount] = useState(null);
  const [txns, setTxns] = useState([]);
  const [loading, setLoading] = useState(true);

  const [err, setErr] = useState("");
  const [warn, setWarn] = useState("");

  const totals = useMemo(() => {
    let debit = 0, credit = 0;
    txns.forEach((t) => {
      const amt = Number(t.amount || 0);
      if ((t.type || "").toUpperCase() === "DEBIT") debit += amt;
      else credit += amt;
    });
    return { debit, credit };
  }, [txns]);

  const load = async () => {
    setErr(""); setWarn(""); setLoading(true);
    try {
      if (useMock) {
        setAccount(mockAccount);
        setTxns(mockTransactions);
        return;
      }
      const a = await getMyAccount();
      const t = await getMyTransactions(10);
      setAccount(a);
      setTxns(Array.isArray(t) ? t : []);
    } catch (e) {
      const d = e?.response?.data?.detail;
      if (d?.code === "STEP_UP_REQUIRED") {
        setWarn(d.message);
      } else if (d?.code === "ACCESS_DENIED") {
        setWarn(d.message);
      } else {
        setErr(d?.message || d || e.message || "Failed");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [useMock]);

  return (
    <Box sx={{ px: 3, py: 2 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Box>
          <Typography variant="h5" fontWeight={900}>Banking (Read)</Typography>
          <Typography variant="body2" sx={{ opacity: 0.75 }}>
            Overview + transactions. Write/Transfer are separate pages.
          </Typography>
        </Box>

        <Stack direction="row" spacing={1}>
          <Button variant="outlined" startIcon={<ReceiptLongRoundedIcon />} onClick={load}>
            Refresh
          </Button>
          <Button variant="contained" startIcon={<SwapHorizRoundedIcon />} onClick={() => navigate("/agent/banking/transfer")}>
            Transfer
          </Button>
        </Stack>
      </Stack>

      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid size={{ xs: 12, md: 4 }}>
          <TrustBar />
        </Grid>

        <Grid size={{ xs: 12, md: 8 }}>
          {(err || warn) && (
            <Alert severity={err ? "error" : "warning"} sx={{ mb: 2 }}>
              {String(err || warn)}
            </Alert>
          )}

          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Stack direction="row" spacing={1.5} alignItems="center">
                <AccountBalanceWalletRoundedIcon />
                <Typography variant="h6" fontWeight={900}>Account Summary</Typography>
                {useMock && <Chip size="small" label="Mock Data" color="warning" />}
              </Stack>

              <Divider sx={{ my: 2 }} />

              {loading ? (
                <>
                  <Skeleton height={30} />
                  <Skeleton height={30} width="70%" />
                </>
              ) : (
                <>
                  <Stack direction={{ xs: "column", sm: "row" }} justifyContent="space-between" alignItems={{ xs: "flex-start", sm: "center" }}>
                    <Box>
                      <Typography sx={{ opacity: 0.75 }}>
                        {account?.customer_name} • {account?.account_type}
                      </Typography>
                      <Typography variant="h4" fontWeight={900}>{money(account?.balance, account?.currency || "INR")}</Typography>
                      <Typography variant="body2" sx={{ opacity: 0.8 }}>
                        Available: {money(account?.available_balance, account?.currency || "INR")}
                      </Typography>
                    </Box>

                    <Stack direction="row" spacing={1} sx={{ mt: { xs: 1, sm: 0 } }}>
                      <Chip icon={<ShieldRoundedIcon />} label="Zero-Trust Protected" variant="outlined" />
                      <Chip label={`IFSC: ${account?.ifsc}`} variant="outlined" />
                    </Stack>
                  </Stack>

                  <Divider sx={{ my: 2 }} />

                  <Grid container spacing={2}>
                    <Grid size={{ xs: 12, sm: 6 }}>
                      <Typography variant="caption" sx={{ opacity: 0.7 }}>Account No</Typography>
                      <Typography fontWeight={800}>{account?.account_no}</Typography>
                    </Grid>
                    <Grid size={{ xs: 12, sm: 6 }}>
                      <Typography variant="caption" sx={{ opacity: 0.7 }}>Branch</Typography>
                      <Typography fontWeight={800}>{account?.branch}</Typography>
                    </Grid>
                    <Grid size={{ xs: 12, sm: 6 }}>
                      <Typography variant="caption" sx={{ opacity: 0.7 }}>Total Credit (last 10)</Typography>
                      <Typography fontWeight={900}>{money(totals.credit, account?.currency || "INR")}</Typography>
                    </Grid>
                    <Grid size={{ xs: 12, sm: 6 }}>
                      <Typography variant="caption" sx={{ opacity: 0.7 }}>Total Debit (last 10)</Typography>
                      <Typography fontWeight={900}>{money(totals.debit, account?.currency || "INR")}</Typography>
                    </Grid>
                  </Grid>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Paper sx={{ borderRadius: 3, overflow: "hidden" }}>
        <Box sx={{ px: 2, py: 1.5, display: "flex", justifyContent: "space-between" }}>
          <Typography variant="h6" fontWeight={900}>Recent Transactions</Typography>
          <Button size="small" onClick={() => navigate("/agent/banking/read")}>View all</Button>
        </Box>
        <Divider />
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 900 }}>Date</TableCell>
              <TableCell sx={{ fontWeight: 900 }}>Description</TableCell>
              <TableCell sx={{ fontWeight: 900 }}>Type</TableCell>
              <TableCell sx={{ fontWeight: 900 }} align="right">Amount</TableCell>
              <TableCell sx={{ fontWeight: 900 }}>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading
              ? Array.from({ length: 6 }).map((_, i) => (
                <TableRow key={i}><TableCell colSpan={5}><Skeleton height={22} /></TableCell></TableRow>
              ))
              : txns.map((t) => (
                <TableRow key={t.id} hover>
                  <TableCell>{t.date ? new Date(t.date).toLocaleString() : "-"}</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>{t.description}</TableCell>
                  <TableCell>
                    <Chip size="small" label={t.type || "DEBIT"} sx={{ borderRadius: 2 }} />
                  </TableCell>
                  <TableCell align="right" sx={{ fontWeight: 900 }}>{money(t.amount, account?.currency || "INR")}</TableCell>
                  <TableCell>
                    <Chip size="small" label={t.status || "SUCCESS"} color={t.status === "FAILED" ? "error" : "success"} />
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
      </Paper>
    </Box>
  );
}
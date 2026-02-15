import { useEffect, useState } from "react";
import { Box, Card, CardContent, Typography, Table, TableHead, TableRow, TableCell, TableBody, Alert } from "@mui/material";
import { getMyTransactions } from "../../services/bankingApi";

export default function BankingTransactions() {
  const [rows, setRows] = useState([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => {
      try {
        setErr("");
        const data = await getMyTransactions(50);
        setRows(Array.isArray(data) ? data : []);
      } catch (e) {
        setErr(e?.response?.data?.detail || e?.message || "Failed to load transactions");
      }
    })();
  }, []);

  // ✅ LIVE FEED (optional)
  useEffect(() => {
    const host = window.location.hostname;
    const ws = new WebSocket(`ws://${host}:8000/ws/banking`);

    ws.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data);
        if (msg.event === "BANK_TXN") {
          setRows((prev) => [
            { id: "live-" + Date.now(), to_owner: msg.to, amount: msg.amount, status: msg.status, created_at: msg.time },
            ...prev,
          ].slice(0, 50));
        }
      } catch {}
    };

    return () => ws.close();
  }, []);

  return (
    <Box sx={{ display: "grid", gap: 2 }}>
      {err && <Alert severity="error">{err}</Alert>}

      <Card>
        <CardContent>
          <Typography variant="h6" fontWeight="bold">Recent Transactions</Typography>

          <Table size="small" sx={{ mt: 2 }}>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>To</TableCell>
                <TableCell>Amount</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {rows.map((r) => (
                <TableRow key={r.id}>
                  <TableCell>{String(r.created_at || "")}</TableCell>
                  <TableCell>{r.to_owner}</TableCell>
                  <TableCell>₹ {Number(r.amount).toFixed(2)}</TableCell>
                  <TableCell>{r.status}</TableCell>
                </TableRow>
              ))}

              {rows.length === 0 && !err && (
                <TableRow>
                  <TableCell colSpan={4}>
                    <Typography color="text.secondary">No transactions yet.</Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </Box>
  );
}
import { useState } from "react";
import { Box, Button, Card, CardContent, TextField, Typography } from "@mui/material";
import { transferMoney } from "../../services/bankingApi";

export default function BankingTransfer() {
  const [to, setTo] = useState("");
  const [amount, setAmount] = useState("100");

  const send = async () => {
    const res = await transferMoney({ to_owner: to, amount: Number(amount) });
    alert(`Transfer: ${res.status}`);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Card sx={{ borderRadius: 3 }}>
        <CardContent>
          <Typography variant="h6">Transactions (TRANSFER)</Typography>
          <TextField fullWidth label="To Owner" sx={{ mt: 2 }} value={to} onChange={(e) => setTo(e.target.value)} />
          <TextField fullWidth label="Amount" sx={{ mt: 2 }} value={amount} onChange={(e) => setAmount(e.target.value)} />
          <Button sx={{ mt: 2 }} variant="contained" onClick={send}>Transfer</Button>
        </CardContent>
      </Card>
    </Box>
  );
}
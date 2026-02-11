import { useEffect, useState } from "react";
import { Box, Card, CardContent, Typography } from "@mui/material";
import { listAccounts } from "../../services/bankingApi";

export default function BankingRead() {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    (async () => {
      const data = await listAccounts();
      setRows(data);
    })();
  }, []);

  return (
    <Box sx={{ p: 3 }}>
      <Card sx={{ borderRadius: 3 }}>
        <CardContent>
          <Typography variant="h6">Banking DB (READ)</Typography>

          {rows.map((r) => (
            <Typography key={r.id} sx={{ mt: 1 }}>
              {r.owner} → Balance: {r.balance}
            </Typography>
          ))}
        </CardContent>
      </Card>
    </Box>
  );
}
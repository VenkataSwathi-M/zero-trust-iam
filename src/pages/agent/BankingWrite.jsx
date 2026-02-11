import { Box, Card, CardContent, Typography } from "@mui/material";

export default function BankingWrite() {
  return (
    <Box sx={{ p: 3, display: "flex", justifyContent: "center" }}>
      <Card sx={{ width: 520, borderRadius: 3 }}>
        <CardContent>
          <Typography variant="h6" fontWeight="bold">
            Banking Write Page
          </Typography>
          <Typography sx={{ mt: 1 }} color="text.secondary">
            (Next: insert/update actions will come here)
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}
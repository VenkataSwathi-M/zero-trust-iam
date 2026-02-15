import { Card, CardContent, Typography, LinearProgress, Stack, Chip } from "@mui/material";
import useTrustStream from "../hooks/useTrustStream";

export default function TrustBarWS() {
  const { trust, status } = useTrustStream();

  const eff = Number(trust?.effective_trust ?? 0);
  const pct = Math.round(eff * 100);

  return (
    <Card sx={{ borderRadius: 3 }}>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
          <Typography fontWeight={900}>Trust Score (Live)</Typography>
          <Chip
            size="small"
            color={status === "open" ? "success" : "warning"}
            label={status === "open" ? "LIVE" : "OFFLINE"}
          />
        </Stack>

        <Typography variant="h6" fontWeight={900} sx={{ mb: 1 }}>
          {pct}%
        </Typography>
        <LinearProgress variant="determinate" value={pct} />

        <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
          <Chip size="small" label={`Access: ${trust?.max_access || "read"}`} />
          <Chip size="small" label={trust?.step_up ? "Step-up OK" : "Step-up required"} />
        </Stack>
      </CardContent>
    </Card>
  );
}
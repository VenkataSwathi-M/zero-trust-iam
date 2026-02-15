import { useEffect, useState } from "react";
import { Card, CardContent, Typography, LinearProgress, Stack, Chip } from "@mui/material";
import { getSessionMe } from "../services/sessionApi";

export default function TrustBar() {
  const [s, setS] = useState(null);

  useEffect(() => {
    let alive = true;
    const tick = async () => {
      try {
        const data = await getSessionMe();
        if (alive) setS(data);
      } catch {}
    };

    tick();
    const id = setInterval(tick, 2500); // ✅ dynamic
    return () => { alive = false; clearInterval(id); };
  }, []);

  const trust = Number(s?.effective_trust ?? 0);
  const pct = Math.round(trust * 100);

  return (
    <Card sx={{ borderRadius: 3 }}>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
          <Typography fontWeight={900}>Trust Score</Typography>
          <Stack direction="row" spacing={1}>
            <Chip size="small" label={`Access: ${s?.max_access || "read"}`} />
            <Chip size="small" color={s?.step_up ? "success" : "warning"} label={s?.step_up ? "Step-up OK" : "No Step-up"} />
          </Stack>
        </Stack>

        <Typography variant="h6" fontWeight={900} sx={{ mb: 1 }}>{pct}%</Typography>
        <LinearProgress variant="determinate" value={pct} />
        <Typography variant="caption" sx={{ opacity: 0.7 }}>
          Updates automatically every 2.5s (decay + actions).
        </Typography>
      </CardContent>
    </Card>
  );
}
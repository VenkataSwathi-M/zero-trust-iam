import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Card, CardContent, Typography } from "@mui/material";

export default function RiskChart({ events = [] }) {
  // only take access decision events which have risk_score
  const filtered = events
    .filter((e) => e?.event === "ACCESS_DECISION" && e?.risk_score !== undefined)
    .slice(0, 50) // last 50 points (events array is usually newest-first)
    .reverse();   // chart should go left->right old->new

  const data = filtered.map((e, idx) => ({
    name: idx + 1,
    risk: Number(e.risk_score) || 0,
  }));

  return (
    <Card sx={{ borderRadius: 3 }}>
      <CardContent>
        <Typography variant="h6">Live Risk Score</Typography>

        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={data}>
            <XAxis hide />
            <YAxis domain={[0, 1]} />
            <Tooltip />
            <Line type="monotone" dataKey="risk" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
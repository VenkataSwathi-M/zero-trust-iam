import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { Card, CardContent, Typography } from "@mui/material";

export default function RiskChart({ data = [] }) {
  const safe = Array.isArray(data) ? data : [];

  const chartData = safe.map((r, idx) => ({
    index: idx + 1,
    risk: Number(r.risk ?? r.risk_score ?? 0),
    decision: r.decision,
  }));

  return (
    <Card sx={{ borderRadius: 3 }}>
      <CardContent>
        <Typography fontWeight="bold" sx={{ mb: 1 }}>
          Risk Score History
        </Typography>

        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="index" />
            <YAxis domain={[0, 1]} />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="risk"
              stroke="#ff4d4f"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
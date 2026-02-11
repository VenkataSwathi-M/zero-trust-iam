import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Typography } from "@mui/material";

export default function TrustChart({ data = [] }) {
  if (!Array.isArray(data) || data.length === 0) {
    return <Typography>No trust data available</Typography>;
  }

  return (
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={data}>
        <XAxis dataKey="t" hide />
        <YAxis domain={[0, 1]} />
        <Tooltip />
        <Line
          type="monotone"
          dataKey="trust"
          stroke="#2e7d32"
          strokeWidth={2}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
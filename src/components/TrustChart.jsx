import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip } from "recharts";
import { Typography } from "@mui/material";

export default function TrustChart({ data = [] }) {
  if (!data || data.length === 0) {
    return <Typography color="text.secondary">No trust data available</Typography>;
  }

  return (
    <div style={{ width: "100%", height: 260 }}>
      <ResponsiveContainer>
        <LineChart data={data}>
          <XAxis dataKey="t" hide />
          <YAxis domain={[0, 1]} />
          <Tooltip />
          <Line type="monotone" dataKey="trust" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
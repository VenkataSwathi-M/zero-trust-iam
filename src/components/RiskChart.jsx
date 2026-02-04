import {
LineChart,
Line,
XAxis,
YAxis,
Tooltip,
ResponsiveContainer,
} from "recharts";
import { Card, CardContent, Typography } from "@mui/material";

export default function RiskChart({ events }) {
const data = events.map((e, i) => ({
    name: i,
    risk: e.risk_score || 0,
}));

return (
    <Card sx={{ borderRadius: 3 }}>
    <CardContent>
        <Typography variant="h6">Live Risk Score</Typography>
        <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
            <XAxis hide />
            <YAxis />
            <Tooltip />
            <Line
            type="monotone"
            dataKey="risk"
            stroke="#1976d2"
            strokeWidth={2}
            />
        </LineChart>
        </ResponsiveContainer>
    </CardContent>
    </Card>
);
}
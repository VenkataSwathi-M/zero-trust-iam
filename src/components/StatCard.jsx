import { Card, CardContent, Typography } from "@mui/material";

export default function StatCard({ title, value }) {
return (
    <Card sx={{ borderRadius: 3 }}>
    <CardContent>
        <Typography variant="subtitle2" color="text.secondary">
        {title}
        </Typography>
        <Typography variant="h4" fontWeight="bold">
        {value}
        </Typography>
    </CardContent>
    </Card>
);
}
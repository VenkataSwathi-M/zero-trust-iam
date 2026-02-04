import {
Table,
TableHead,
TableRow,
TableCell,
TableBody,
Card,
CardContent,
Typography,
} from "@mui/material";

export default function DecisionTable({ events }) {
return (
    <Card sx={{ borderRadius: 3 }}>
    <CardContent>
        <Typography variant="h6">Live Decisions</Typography>

        <Table size="small">
        <TableHead>
            <TableRow>
            <TableCell>Agent</TableCell>
            <TableCell>Resource</TableCell>
            <TableCell>Decision</TableCell>
            <TableCell>Risk</TableCell>
            </TableRow>
        </TableHead>

        <TableBody>
            {events.map((e, i) => (
            <TableRow key={i}>
                <TableCell>{e.identity_id}</TableCell>
                <TableCell>{e.resource}</TableCell>
                <TableCell
                sx={{
                    color: e.decision === "ALLOW" ? "green" : "red",
                    fontWeight: "bold",
                }}
                >
                {e.decision}
                </TableCell>
                <TableCell>{e.risk_score}</TableCell>
            </TableRow>
            ))}
        </TableBody>
        </Table>
    </CardContent>
    </Card>
);
}
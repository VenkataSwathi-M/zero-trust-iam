import { useEffect, useState } from "react";
import {
  Card, CardContent, Typography, Table, TableHead, TableRow,
  TableCell, TableBody, Alert
} from "@mui/material";
import adminApi from "../services/adminApi"; // adjust path if needed

export default function AuditLogsTable({ agentId }) {
  const [logs, setLogs] = useState([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    if (!agentId) return;

    let alive = true;
    (async () => {
      try {
        setErr("");
        const res = await adminApi.get(`/admin/audit/logs?agent_id=${agentId}&limit=50`);
        const safe = Array.isArray(res?.data) ? res.data : [];
        if (alive) setLogs(safe);
      } catch (e) {
        const msg =
          e?.response?.data?.detail ||
          e?.response?.data?.message ||
          e?.message ||
          "Failed to load audit logs";
        if (alive) setErr(String(msg));
        if (alive) setLogs([]);
      }
    })();

    return () => { alive = false; };
  }, [agentId]);

  return (
    <Card>
      <CardContent>
        <Typography fontWeight="bold">Audit Logs ({agentId})</Typography>

        {err && (
          <Alert severity="error" sx={{ mt: 1 }}>
            {err}
          </Alert>
        )}

        <Table size="small" sx={{ mt: 1 }}>
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Agent</TableCell>
              <TableCell>Event</TableCell>
              <TableCell>Message</TableCell>
            </TableRow>
          </TableHead>

          <TableBody>
            {logs.map((r) => (
              <TableRow key={r.id}>
                <TableCell>{String(r.created_at || "")}</TableCell>
                <TableCell>{r.agent_id}</TableCell>
                <TableCell>{r.event_type}</TableCell>
                <TableCell>{r.message}</TableCell>
              </TableRow>
            ))}

            {logs.length === 0 && !err && (
              <TableRow>
                <TableCell colSpan={4}>
                  <Typography color="text.secondary">No audit logs yet.</Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
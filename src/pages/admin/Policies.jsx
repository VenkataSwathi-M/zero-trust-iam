import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Chip,
  Alert,
} from "@mui/material";
import { getPolicies } from "../../services/adminApi";

function EffectChip({ effect }) {
  const label = String(effect || "").toUpperCase();
  if (label === "ALLOW") return <Chip label="ALLOW" color="success" size="small" />;
  if (label === "DENY") return <Chip label="DENY" color="error" size="small" />;
  return <Chip label={label || "UNKNOWN"} color="warning" size="small" />;
}

export default function Policies() {
  const navigate = useNavigate();
  const [rows, setRows] = useState([]);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  const load = async () => {
    try {
      setErr("");
      setLoading(true);
      const data = await getPolicies();

      // backend might return {policies:[...]} or [...]
      const list = Array.isArray(data) ? data : data?.policies || [];
      setRows(list);
    } catch (e) {
      setErr(
        e?.response?.data?.detail ||
          e?.response?.data?.message ||
          e?.message ||
          "Failed to load policies"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Typography variant="h6" fontWeight="bold">
          Policies
        </Typography>

        <Button variant="contained" onClick={() => navigate("/admin/policies/create")}>
          + Create Policy
        </Button>
      </Box>

      {err && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {String(err)}
        </Alert>
      )}

      <Card sx={{ mt: 2, borderRadius: 3 }}>
        <CardContent>
          <Typography sx={{ mb: 2, opacity: 0.8 }}>
            {loading ? "Loading..." : `Total: ${rows.length}`}
          </Typography>

          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Agent</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Resource</TableCell>
                <TableCell>Action</TableCell>
                <TableCell>Effect</TableCell>

                <TableCell>Min Trust</TableCell>
                <TableCell>Max Risk</TableCell>
                <TableCell>Max Amount</TableCell>
                <TableCell>MFA</TableCell>

                <TableCell>Priority</TableCell>
                <TableCell>Active</TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {rows.map((p) => (
                <TableRow key={p.id || `${p.agent_id}-${p.resource}-${p.action}`}>
                  <TableCell>{p.agent_id}</TableCell>
                  <TableCell>{p.name || "-"}</TableCell>
                  <TableCell>{p.resource}</TableCell>
                  <TableCell>{p.action}</TableCell>
                  <TableCell>
                    <EffectChip effect={p.effect} />
                  </TableCell>

                  <TableCell>{p.min_trust ?? "-"}</TableCell>
                  <TableCell>{p.max_risk ?? "-"}</TableCell>
                  <TableCell>{p.max_amount ?? "-"}</TableCell>
                  <TableCell>{p.require_mfa ? "YES" : "NO"}</TableCell>

                  <TableCell>{p.priority ?? 1}</TableCell>
                  <TableCell>{p.active ? "YES" : "NO"}</TableCell>
                </TableRow>
              ))}

              {rows.length === 0 && !loading && (
                <TableRow>
                  <TableCell colSpan={11} align="center">
                    No policies found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </Box>
  );
}
// src/pages/admin/Dashboard.jsx
import { useEffect, useMemo, useState } from "react";
import {
  Box,
  Card,
  CardContent,
  MenuItem,
  TextField,
  Typography,
  Alert,
} from "@mui/material";
import { useNavigate } from "react-router-dom";

import useDecisionStream from "../../hooks/useDecisionStream";
import TrustChart from "../../components/TrustChart";
import RiskChart from "../../components/RiskChart";
import adminApi from "../../services/adminApi";
import AuditLogsTable from "../../components/AuditLogsTable";

export default function Dashboard() {
  const navigate = useNavigate();
  const { events, trustMap } = useDecisionStream(); // WS live updates

  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState("");

  const [riskHistory, setRiskHistory] = useState([]);
  const [trustHistory, setTrustHistory] = useState([]); // ✅ from DB for selected agent
  const [decisionCounts, setDecisionCounts] = useState({
    ALLOW: 0,
    DENY: 0,
    STEP_UP: 0,
  });
  const [incidents, setIncidents] = useState([]);

  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(true);

  // ✅ initial load (overview)
  useEffect(() => {
    let alive = true;

    (async () => {
      try {
        setErr("");
        setLoading(true);

        const res = await adminApi.get("/admin/metrics/overview");
        const data = res?.data || {};

        const safeAgents = Array.isArray(data.agents) ? data.agents : [];
        const safeIncidents = Array.isArray(data.incidents) ? data.incidents : [];
        const safeDecisionCounts =
          data.decision_counts && typeof data.decision_counts === "object"
            ? { ALLOW: 0, DENY: 0, STEP_UP: 0, ...data.decision_counts }
            : { ALLOW: 0, DENY: 0, STEP_UP: 0 };

        if (!alive) return;

        setAgents(safeAgents);
        setIncidents(safeIncidents);
        setDecisionCounts(safeDecisionCounts);

        // pick first agent by default
        if (safeAgents.length) setSelectedAgent(safeAgents[0].agent_id);
      } catch (e) {
        const status = e?.response?.status;
        const msg =
          e?.response?.data?.detail ||
          e?.response?.data?.message ||
          e?.message ||
          "Failed to load dashboard";

        if (!alive) return;

        setErr(String(msg));

        if (status === 401) {
          localStorage.removeItem("admin_token");
          navigate("/admin/login");
        }

        setAgents([]);
        setIncidents([]);
        setDecisionCounts({ ALLOW: 0, DENY: 0, STEP_UP: 0 });
      } finally {
        if (alive) setLoading(false);
      }
    })();

    return () => {
      alive = false;
    };
  }, [navigate]);

  // ✅ load selected agent risk history
  useEffect(() => {
    if (!selectedAgent) return;
    let alive = true;

    (async () => {
      try {
        const res = await adminApi.get(`/admin/metrics/risk-history/${selectedAgent}`);
        const safe = Array.isArray(res?.data) ? res.data : [];
        if (alive) setRiskHistory(safe);
      } catch {
        if (alive) setRiskHistory([]);
      }
    })();

    return () => {
      alive = false;
    };
  }, [selectedAgent]);

  // ✅ load selected agent trust history (DB) for TrustChart
  useEffect(() => {
    if (!selectedAgent) return;
    let alive = true;

    (async () => {
      try {
        const res = await adminApi.get(`/admin/metrics/trust-history/${selectedAgent}`, {
          params: { limit: 60 },
        });
        const safe = Array.isArray(res?.data) ? res.data : [];
        if (alive) setTrustHistory(safe);
      } catch {
        if (alive) setTrustHistory([]);
      }
    })();

    return () => {
      alive = false;
    };
  }, [selectedAgent]);

  // ✅ Live Trust number: prefer WS, fallback to last DB trustHistory point
  const liveTrust = useMemo(() => {
    const wsTrust = trustMap?.[selectedAgent];
    if (wsTrust !== undefined && wsTrust !== null) return wsTrust;

    const last = trustHistory?.[trustHistory.length - 1];
    return last?.trust;
  }, [trustMap, selectedAgent, trustHistory]);

  // ✅ live decision counts from WS events
  useEffect(() => {
    const latest = events?.[0];
    if (!latest || latest.event !== "ACCESS_DECISION") return;

    setDecisionCounts((prev) => {
      const copy = { ...prev };
      if (copy[latest.decision] !== undefined) copy[latest.decision] += 1;
      return copy;
    });
  }, [events]);

  return (
    <Box sx={{ display: "grid", gap: 2 }}>
      {err && <Alert severity="error">{err}</Alert>}

      <Card>
        <CardContent sx={{ display: "flex", gap: 2, alignItems: "center" }}>
          <Typography fontWeight="bold">Admin Dashboard</Typography>

          <TextField
            select
            size="small"
            label="Agent"
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value)}
            sx={{ minWidth: 250 }}
            disabled={loading || agents.length === 0}
          >
            {agents.map((a) => (
              <MenuItem key={a.agent_id} value={a.agent_id}>
                {a.agent_id}
              </MenuItem>
            ))}
          </TextField>

          <Typography sx={{ ml: "auto" }}>
            Live Trust: <b>{liveTrust ?? "—"}</b>
          </Typography>
        </CardContent>
      </Card>

      <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 2 }}>
        <Card>
          <CardContent>
            <Typography>ALLOW</Typography>
            <Typography variant="h5">{decisionCounts?.ALLOW ?? 0}</Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography>DENY</Typography>
            <Typography variant="h5">{decisionCounts?.DENY ?? 0}</Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography>STEP_UP</Typography>
            <Typography variant="h5">{decisionCounts?.STEP_UP ?? 0}</Typography>
          </CardContent>
        </Card>
      </Box>

      <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 2 }}>
        <Card>
          <CardContent>
            <Typography fontWeight="bold">Trust Score (Selected Agent)</Typography>
            {/* ✅ Use DB trustHistory so chart shows seeded data */}
            <TrustChart data={Array.isArray(trustHistory) ? trustHistory : []} />
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography fontWeight="bold">Risk Score History (Selected Agent)</Typography>
            <RiskChart data={Array.isArray(riskHistory) ? riskHistory : []} />
          </CardContent>
        </Card>
      </Box>

      <Card>
        <CardContent>
          <Typography fontWeight="bold">Incident Feed (Latest)</Typography>
          <Box sx={{ mt: 1 }}>
            {(Array.isArray(incidents) ? incidents : [])
              .slice(0, 10)
              .map((i, idx) => (
                <Typography key={idx} sx={{ mb: 0.5 }}>
                  <b>{i.agent_id}</b> • {i.event_type} • {i.message}
                </Typography>
              ))}

            {(!incidents || incidents.length === 0) && (
              <Typography color="text.secondary" sx={{ mt: 1 }}>
                No incidents yet.
              </Typography>
            )}
          </Box>
        </CardContent>
      </Card>

      {/* ✅ Optional: If you want audit logs filtered by selected agent,
          update AuditLogsTable to accept agentId prop and use it */}
      <AuditLogsTable agentId={selectedAgent} />
    </Box>
  );
}
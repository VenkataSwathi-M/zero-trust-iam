import { useEffect, useMemo, useState } from "react";
import { Box, Card, CardContent, MenuItem, TextField, Typography, Alert } from "@mui/material";
import useDecisionStream from "../../hooks/useDecisionStream";
import TrustChart from "../../components/TrustChart";
import RiskChart from "../../components/RiskChart";
import adminApi from "../../services/adminApi";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const navigate = useNavigate();
  const { events, trustMap } = useDecisionStream();

  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState("");
  const [riskHistory, setRiskHistory] = useState([]);
  const [trustSeries, setTrustSeries] = useState([]);
  const [decisionCounts, setDecisionCounts] = useState({ ALLOW: 0, DENY: 0, STEP_UP: 0 });
  const [incidents, setIncidents] = useState([]);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(true);

  // initial load
  useEffect(() => {
    let alive = true;

    (async () => {
      try {
        setErr("");
        setLoading(true);

        const res = await adminApi.get("/admin/metrics/overview");
        const data = res?.data || {};

        // ✅ always fallback to safe types
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

        // ✅ If unauthorized, go back to admin login
        if (status === 401) {
          localStorage.removeItem("admin_token");
          navigate("/admin/login");
        }

        // ✅ keep state safe so UI doesn't crash
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

  // load risk history when agent changes
  useEffect(() => {
    if (!selectedAgent) return;
    let alive = true;

    (async () => {
      try {
        const res = await adminApi.get(`/admin/metrics/risk-history/${selectedAgent}`);
        const safe = Array.isArray(res?.data) ? res.data : [];
        if (alive) setRiskHistory(safe);
      } catch (e) {
        if (alive) setRiskHistory([]); // ✅ don't crash chart
      }
    })();

    return () => {
      alive = false;
    };
  }, [selectedAgent]);

  // live trust series for chart (from WS updates)
  useEffect(() => {
    if (!selectedAgent) return;
    const trust = trustMap?.[selectedAgent];
    if (trust === undefined || trust === null) return;

    setTrustSeries((prev) => {
      const next = [...prev, { t: Date.now(), trust }];
      return next.slice(-60);
    });
  }, [trustMap, selectedAgent]);

  // live decision counts (from WS events)
  useEffect(() => {
    const latest = events?.[0];
    if (!latest || latest.event !== "ACCESS_DECISION") return;

    setDecisionCounts((prev) => {
      const copy = { ...prev };
      if (copy[latest.decision] !== undefined) copy[latest.decision] += 1;
      return copy;
    });
  }, [events]);

  const liveTrust = useMemo(() => trustMap?.[selectedAgent], [trustMap, selectedAgent]);

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
            <Typography fontWeight="bold">Live Trust Score</Typography>
            <TrustChart data={Array.isArray(trustSeries) ? trustSeries : []} />
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography fontWeight="bold">Risk Score History</Typography>
            <RiskChart data={Array.isArray(riskHistory) ? riskHistory : []} />
          </CardContent>
        </Card>
      </Box>

      <Card>
        <CardContent>
          <Typography fontWeight="bold">Incident Feed (Latest)</Typography>
          <Box sx={{ mt: 1 }}>
            {(Array.isArray(incidents) ? incidents : []).slice(0, 10).map((i, idx) => (
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
    </Box>
  );
}
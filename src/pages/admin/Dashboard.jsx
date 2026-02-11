import { useEffect, useMemo, useState } from "react";
import { Box, Card, CardContent, MenuItem, TextField, Typography } from "@mui/material";
import useDecisionStream from "../../hooks/useDecisionStream";
import TrustChart from "../../components/TrustChart";
import RiskChart from "../../components/RiskChart";
import adminApi from "../../services/adminApi";

export default function Dashboard() {
  const { events, trustMap } = useDecisionStream();

  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState("");
  const [riskHistory, setRiskHistory] = useState([]);
  const [trustSeries, setTrustSeries] = useState([]);
  const [decisionCounts, setDecisionCounts] = useState({ ALLOW: 0, DENY: 0, STEP_UP: 0 });
  const [incidents, setIncidents] = useState([]);

  // initial load
  useEffect(() => {
    (async () => {
      const res = await adminApi.get("/admin/metrics/overview");
      setAgents(res.data.agents);
      setDecisionCounts(res.data.decision_counts);
      setIncidents(res.data.incidents);

      if (res.data.agents?.length) {
        setSelectedAgent(res.data.agents[0].agent_id);
      }
    })();
  }, []);

  // load risk history when agent changes
  useEffect(() => {
    if (!selectedAgent) return;

    (async () => {
      const res = await adminApi.get(`/admin/metrics/risk-history/${selectedAgent}`);
      setRiskHistory(res.data);
    })();
  }, [selectedAgent]);

  // live trust series for chart (from WS updates)
  useEffect(() => {
    if (!selectedAgent) return;
    const trust = trustMap[selectedAgent];
    if (trust === undefined) return;

    setTrustSeries((prev) => {
      const next = [...prev, { t: Date.now(), trust }];
      return next.slice(-60); // last 60 points
    });
  }, [trustMap, selectedAgent]);

  // live decision counts (from WS events)
  useEffect(() => {
    const latest = events[0];
    if (!latest || latest.event !== "ACCESS_DECISION") return;

    setDecisionCounts((prev) => {
      const copy = { ...prev };
      if (copy[latest.decision] !== undefined) copy[latest.decision] += 1;
      return copy;
    });
  }, [events]);

  const liveTrust = useMemo(() => trustMap[selectedAgent], [trustMap, selectedAgent]);

  return (
    <Box sx={{ display: "grid", gap: 2 }}>
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
        <Card><CardContent><Typography>ALLOW</Typography><Typography variant="h5">{decisionCounts.ALLOW}</Typography></CardContent></Card>
        <Card><CardContent><Typography>DENY</Typography><Typography variant="h5">{decisionCounts.DENY}</Typography></CardContent></Card>
        <Card><CardContent><Typography>STEP_UP</Typography><Typography variant="h5">{decisionCounts.STEP_UP}</Typography></CardContent></Card>
      </Box>

      <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 2 }}>
        <Card>
          <CardContent>
            <Typography fontWeight="bold">Live Trust Score</Typography>
            <TrustChart data={trustSeries} />
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography fontWeight="bold">Risk Score History</Typography>
            <RiskChart data={riskHistory} />
          </CardContent>
        </Card>
      </Box>

      <Card>
        <CardContent>
          <Typography fontWeight="bold">Incident Feed (Latest)</Typography>
          <Box sx={{ mt: 1 }}>
            {incidents.slice(0, 10).map((i, idx) => (
              <Typography key={idx} sx={{ mb: 0.5 }}>
                <b>{i.agent_id}</b> • {i.event_type} • {i.message}
              </Typography>
            ))}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
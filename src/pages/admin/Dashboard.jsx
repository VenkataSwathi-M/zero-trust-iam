import { Box, Grid } from "@mui/material";
import useDecisionStream from "../../hooks/useDecisionStream";
import StatCard from "../../components/StatCard";
import RiskChart from "../../components/RiskChart";
import DecisionTable from "../../components/DecisionTable";

export default function AdminDashboard() {
  const events = useDecisionStream();

  const total = events.length;
  const allowed = events.filter(e => e.decision === "ALLOW").length;
  const denied = events.filter(e => e.decision === "DENY").length;
  const mfa = events.filter(e => e.decision === "STEP_UP").length;

  return (
    <Box sx={{ p: 3 }}>
      {/* ================= STAT CARDS ================= */}
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard title="Total Requests" value={total} />
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard title="Allowed" value={allowed} />
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard title="Denied" value={denied} />
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard title="MFA / Step-Up" value={mfa} />
        </Grid>
      </Grid>

      {/* ================= RISK CHART ================= */}
      <Grid container spacing={2} sx={{ mt: 3 }}>
        <Grid size={{ xs: 12 }}>
          <RiskChart events={events} />
        </Grid>
      </Grid>

      {/* ================= DECISION TABLE ================= */}
      <Box sx={{ mt: 3 }}>
        <DecisionTable events={events} />
      </Box>
    </Box>
  );
}
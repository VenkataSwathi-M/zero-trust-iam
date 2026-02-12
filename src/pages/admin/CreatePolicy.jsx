import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  MenuItem,
  Alert,
  FormControlLabel,
  Checkbox,
} from "@mui/material";
import { createPolicy } from "../../services/adminApi";

const RISK_LEVELS = ["LOW", "MEDIUM", "HIGH"];
const EFFECTS = ["ALLOW", "DENY", "STEP_UP"];

export default function CreatePolicy() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    agent_id: "ALL",
    name: "",
    resource: "accounts",
    action: "read",
    effect: "ALLOW",
    min_trust: 0.4,
    max_risk: "HIGH",
    max_amount: "",
    require_mfa: false,
    priority: 1,
    active: true,
  });

  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [ok, setOk] = useState("");

  const onChange = (key) => (e) => {
    const value =
      e.target.type === "checkbox" ? e.target.checked : e.target.value;
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const submit = async () => {
    try {
      setErr("");
      setOk("");
      setLoading(true);

      // sanitize numeric fields
      const payload = {
        ...form,
        min_trust: Number(form.min_trust),
        priority: Number(form.priority),
        max_amount:
          form.max_amount === "" || form.max_amount === null
            ? null
            : Number(form.max_amount),
      };

      if (!payload.name?.trim()) throw new Error("Policy name is required");
      if (!payload.resource?.trim()) throw new Error("Resource is required");
      if (!payload.action?.trim()) throw new Error("Action is required");
      if (Number.isNaN(payload.min_trust)) throw new Error("min_trust invalid");
      if (payload.min_trust < 0 || payload.min_trust > 1)
        throw new Error("min_trust must be between 0.0 and 1.0");

      await createPolicy(payload);

      setOk("Policy created successfully.");
      setTimeout(() => navigate("/admin/policies"), 600);
    } catch (e) {
      setErr(
        e?.response?.data?.detail ||
          e?.response?.data?.message ||
          e?.message ||
          "Failed"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
      <Card sx={{ width: 720, borderRadius: 3 }}>
        <CardContent>
          <Typography variant="h6" fontWeight="bold">
            Create Policy
          </Typography>

          {err && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {String(err)}
            </Alert>
          )}
          {ok && (
            <Alert severity="success" sx={{ mt: 2 }}>
              {String(ok)}
            </Alert>
          )}

          <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 2, mt: 2 }}>
            <TextField
              label="Policy Name"
              value={form.name}
              onChange={onChange("name")}
              fullWidth
            />

            <TextField
              label="Agent ID (use ALL for global)"
              value={form.agent_id}
              onChange={onChange("agent_id")}
              fullWidth
            />

            <TextField
              label="Resource"
              value={form.resource}
              onChange={onChange("resource")}
              fullWidth
              placeholder="accounts / transactions / banking_db"
            />

            <TextField
              label="Action"
              value={form.action}
              onChange={onChange("action")}
              fullWidth
              placeholder="read / write / transfer"
            />

            <TextField
              select
              label="Effect"
              value={form.effect}
              onChange={onChange("effect")}
              fullWidth
            >
              {EFFECTS.map((x) => (
                <MenuItem key={x} value={x}>
                  {x}
                </MenuItem>
              ))}
            </TextField>

            <TextField
              label="Min Trust (0.0 - 1.0)"
              type="number"
              inputProps={{ step: 0.01, min: 0, max: 1 }}
              value={form.min_trust}
              onChange={onChange("min_trust")}
              fullWidth
            />

            <TextField
              select
              label="Max Risk Allowed"
              value={form.max_risk}
              onChange={onChange("max_risk")}
              fullWidth
            >
              {RISK_LEVELS.map((x) => (
                <MenuItem key={x} value={x}>
                  {x}
                </MenuItem>
              ))}
            </TextField>

            <TextField
              label="Max Amount (optional)"
              type="number"
              value={form.max_amount}
              onChange={onChange("max_amount")}
              fullWidth
            />

            <TextField
              label="Priority (higher wins)"
              type="number"
              inputProps={{ min: 1 }}
              value={form.priority}
              onChange={onChange("priority")}
              fullWidth
            />

            <Box sx={{ display: "flex", flexDirection: "column" }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={form.require_mfa}
                    onChange={onChange("require_mfa")}
                  />
                }
                label="Require MFA (OTP)"
              />
              <FormControlLabel
                control={
                  <Checkbox checked={form.active} onChange={onChange("active")} />
                }
                label="Active"
              />
            </Box>
          </Box>

          <Box sx={{ display: "flex", gap: 2, mt: 3 }}>
            <Button variant="contained" onClick={submit} disabled={loading}>
              {loading ? "Saving..." : "Create Policy"}
            </Button>
            <Button variant="outlined" onClick={() => navigate("/admin/policies")}>
              Cancel
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
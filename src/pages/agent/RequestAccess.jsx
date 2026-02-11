import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Box, Button, Card, CardContent, MenuItem, Typography, TextField } from "@mui/material";
import { requestAccess } from "../../services/agentApi";

export default function RequestAccess() {
  const navigate = useNavigate();

  const [resource] = useState("banking"); // fixed
  const [action, setAction] = useState("read");
  const [result, setResult] = useState(null);

  const submit = async () => {
    try {
      const res = await requestAccess(resource, action);
      setResult(res);

      if (res.decision === "ALLOW") {
        if (action === "read") navigate("/agent/banking/read");
        if (action === "write") navigate("/agent/banking/write");
        if (action === "transfer") navigate("/agent/banking/transfer");
      }

      if (res.decision === "STEP_UP") {
        alert("MFA required (STEP_UP). Verify OTP then retry.");
        // you can navigate to an MFA page if you have it
      }

      if (res.decision === "DENY") {
        alert(`Denied: ${res.reason || "policy"}`);
      }
    } catch (err) {
      alert(err?.response?.data?.detail || "Request failed");
    }
  };

  return (
    <Box sx={{ p: 3, display: "flex", justifyContent: "center" }}>
      <Card sx={{ width: 420, borderRadius: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Request Banking Access
          </Typography>

          <TextField
            select
            fullWidth
            label="Action"
            value={action}
            onChange={(e) => setAction(e.target.value)}
            sx={{ mt: 2 }}
          >
            <MenuItem value="read">Read</MenuItem>
            <MenuItem value="write">Write</MenuItem>
            <MenuItem value="transfer">Transfer</MenuItem>
          </TextField>

          <Button fullWidth sx={{ mt: 3 }} variant="contained" onClick={submit}>
            Request Access
          </Button>

          {result && (
            <Typography sx={{ mt: 2, fontWeight: "bold" }}>
              Decision: {result.decision} | Risk: {result.risk_score} ({result.risk_level})
            </Typography>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
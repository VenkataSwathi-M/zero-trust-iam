import { useState } from "react";
import {
  Box,
  Button,
  Card,
  CardContent,
  MenuItem,
  Typography,
  TextField
} from "@mui/material";
import { requestAccess } from "../../services/agentApi";

export default function RequestAccess() {
  const [resource] = useState("banking"); // fixed resource (Zero Trust service)
  const [action, setAction] = useState("read");
  const [result, setResult] = useState(null);

  const submit = async () => {
    const res = await requestAccess(resource, action);
    setResult(res);
  };

  return (
    <Box
      sx={{
        p: 3,
        display: "flex",
        justifyContent: "center"
      }}
    >
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

          <Button
            fullWidth
            sx={{ mt: 3 }}
            variant="contained"
            onClick={submit}
          >
            Request Access
          </Button>

          {result && (
            <Typography
              sx={{ mt: 2, fontWeight: "bold" }}
              color={
                result.decision === "ALLOW"
                  ? "success.main"
                  : result.decision === "STEP_UP"
                  ? "warning.main"
                  : "error.main"
              }
            >
              Decision: {result.decision}
            </Typography>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
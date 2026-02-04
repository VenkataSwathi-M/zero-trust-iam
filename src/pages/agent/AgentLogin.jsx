import { useState } from "react";
import { Box, Button, Card, CardContent, TextField, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { agentLogin } from "../../services/agentApi";

export default function AgentLogin() {
  const [agentId, setAgentId] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const login = async () => {
    try {
      setError("");
      const res = await agentLogin(agentId);

      // Store Zero Trust session token
      localStorage.setItem("token", res.access_token);

      navigate("/agent/dashboard");
    } catch (err) {
      setError("Invalid Agent ID");
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center"
      }}
    >
      <Card sx={{ width: 360, borderRadius: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Agent Login
          </Typography>

          <TextField
            fullWidth
            label="Agent ID"
            value={agentId}
            onChange={(e) => setAgentId(e.target.value)}
            sx={{ mt: 2 }}
          />

          {error && (
            <Typography color="error" sx={{ mt: 1 }}>
              {error}
            </Typography>
          )}

          <Button
            fullWidth
            sx={{ mt: 3 }}
            variant="contained"
            onClick={login}
          >
            Login
          </Button>
        </CardContent>
      </Card>
    </Box>
  );
}
import { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography
} from "@mui/material";

import { createAgent } from "../../services/adminApi";

export default function CreateAgent() {
  const [agentId, setAgentId] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [maxAccess, setMaxAccess] = useState("read");
  const [trust, setTrust] = useState(0.5);
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    try {
      setLoading(true);

      await createAgent({
        agent_id: agentId,
        email,
        password,
        max_access: maxAccess,
        trust_level: trust
      });

      alert("Agent created successfully");

      setAgentId("");
      setEmail("");
      setPassword("");
      setMaxAccess("read");
      setTrust(0.5);

    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "Failed to create agent");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box p={3}>
      <Card sx={{ maxWidth: 500 }}>
        <CardContent>
          <Typography variant="h6">Create Agent</Typography>

          <TextField
            label="Agent ID"
            fullWidth
            sx={{ mt: 2 }}
            value={agentId}
            onChange={e => setAgentId(e.target.value)}
          />

          <TextField
            label="Email"
            type="email"
            fullWidth
            sx={{ mt: 2 }}
            value={email}
            onChange={e => setEmail(e.target.value)}
          />

          <TextField
            label="Password"
            type="password"
            fullWidth
            sx={{ mt: 2 }}
            value={password}
            onChange={e => setPassword(e.target.value)}
          />

          <TextField
            label="Max Access (read / write / transfer)"
            fullWidth
            sx={{ mt: 2 }}
            value={maxAccess}
            onChange={e => setMaxAccess(e.target.value)}
          />

          <TextField
            label="Initial Trust (0–1)"
            type="number"
            inputProps={{ min: 0, max: 1, step: 0.1 }}
            fullWidth
            sx={{ mt: 2 }}
            value={trust}
            onChange={e => setTrust(Number(e.target.value))}
          />

          <Button
            variant="contained"
            fullWidth
            sx={{ mt: 3 }}
            disabled={loading}
            onClick={handleCreate}
          >
            {loading ? "Creating..." : "Create Agent"}
          </Button>
        </CardContent>
      </Card>
    </Box>
  );
}
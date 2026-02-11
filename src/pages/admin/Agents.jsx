import { useEffect, useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableRow,
  TableCell,
  TableHead,
  TableBody,
  Button
} from "@mui/material";
import { useNavigate } from "react-router-dom";

import { getAgents } from "../../services/adminApi";

export default function Agents() {
  const [agents, setAgents] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      const data = await getAgents();
      setAgents(data);
    } catch (err) {
      console.error("Load agents failed", err);
      alert("Failed to load agents");
    }
  };

  return (
    <Box p={3}>
      {/* Header */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 2
        }}
      >
        <Typography variant="h6">Registered Agents</Typography>

        <Button
          variant="contained"
          onClick={() => navigate("/admin/agents/create")}
        >
          Create Agent
        </Button>
      </Box>

      {/* Agents Table */}
      <Card>
        <CardContent>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Agent ID</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Max Access</TableCell>
                <TableCell>Trust Level</TableCell>
                <TableCell>MFA</TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {agents.map(agent => (
                <TableRow key={agent.agent_id}>
                  <TableCell>{agent.agent_id}</TableCell>
                  <TableCell>{agent.email}</TableCell>
                  <TableCell>{agent.max_access}</TableCell>
                  <TableCell>{agent.trust_level}</TableCell>
                  <TableCell>
                    {agent.mfa_enabled ? "Enabled" : "Disabled"}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {agents.length === 0 && (
            <Typography color="text.secondary" sx={{ mt: 2 }}>
              No agents created yet
            </Typography>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
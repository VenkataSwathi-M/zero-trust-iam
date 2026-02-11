import { useEffect, useState } from "react";
import {
  Box, Card, CardContent, TextField, Button,
  Typography, Table, TableHead, TableRow, TableCell, TableBody
} from "@mui/material";
import { createPolicy, getPolicies } from "../../services/adminApi";

export default function Policies() {
  const [form, setForm] = useState({
    name: "",
    resource: "",
    action: "",
    effect: "allow"
  });
  const [policies, setPolicies] = useState([]);

  useEffect(() => {
    getPolicies().then(setPolicies);
  }, []);

  const handleCreate = async () => {
    const policy = await createPolicy(form);
    setPolicies(p => [...p, policy]);
    setForm({ name: "", resource: "", action: "", effect: "allow" });
  };

  return (
    <Box p={3}>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6">Create Policy</Typography>

          {["name", "resource", "action", "effect"].map(f => (
            <TextField
              key={f}
              label={f.toUpperCase()}
              fullWidth
              sx={{ mt: 2 }}
              value={form[f]}
              onChange={e => setForm({ ...form, [f]: e.target.value })}
            />
          ))}

          <Button fullWidth variant="contained" sx={{ mt: 2 }} onClick={handleCreate}>
            Create Policy
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6">Policies</Typography>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Resource</TableCell>
                <TableCell>Action</TableCell>
                <TableCell>Effect</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {policies.map(p => (
                <TableRow key={p.id}>
                  <TableCell>{p.name}</TableCell>
                  <TableCell>{p.resource}</TableCell>
                  <TableCell>{p.action}</TableCell>
                  <TableCell>{p.effect}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </Box>
  );
}
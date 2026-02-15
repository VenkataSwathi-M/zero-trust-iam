import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Divider,
  Alert,
} from "@mui/material";
import SecurityIcon from "@mui/icons-material/Security";
import axios from "axios";

export default function AdminLogin() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setErr("");
    setLoading(true);

    try {
      // ✅ backend call (you must implement this route in FastAPI)
      const res = await axios.post("http://192.168.31.211:8000/admin/auth/login", {
        email,
        password,
      });

      const token = res?.data?.access_token;
      if (!token) throw new Error("Backend did not return access_token");

      // ✅ IMPORTANT: store admin token for adminApi interceptor
      localStorage.setItem("admin_token", token);

      navigate("/admin/dashboard");
    } catch (e2) {
      const msg =
        e2?.response?.data?.detail ||
        e2?.response?.data?.message ||
        e2?.message ||
        "Login failed";
      setErr(String(msg));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #0f2027, #203a43, #2c5364)",
      }}
    >
      <Paper elevation={10} sx={{ width: 380, p: 4 }}>
        <Box sx={{ textAlign: "center", mb: 2 }}>
          <SecurityIcon color="primary" sx={{ fontSize: 40 }} />
          <Typography variant="h5" fontWeight="bold">
            Admin Login
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Zero Trust IAM Control Panel
          </Typography>
        </Box>

        <Divider sx={{ mb: 3 }} />

        {err && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {err}
          </Alert>
        )}

        <Box component="form" onSubmit={handleLogin}>
          <TextField
            label="Admin Email"
            type="email"
            fullWidth
            required
            margin="normal"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <TextField
            label="Password"
            type="password"
            fullWidth
            required
            margin="normal"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <Button
            type="submit"
            variant="contained"
            fullWidth
            disabled={loading || !email || !password}
            sx={{ mt: 3, py: 1.2 }}
          >
            {loading ? "Logging in..." : "Login"}
          </Button>
        </Box>

        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ mt: 3, display: "block", textAlign: "center" }}
        >
          © Zero Trust IAM • Admin Access Only
        </Typography>
      </Paper>
    </Box>
  );
}
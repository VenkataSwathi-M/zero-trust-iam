import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
Box,
Paper,
TextField,
Button,
Typography,
Divider
} from "@mui/material";
import SecurityIcon from "@mui/icons-material/Security";

export default function AdminLogin() {
const navigate = useNavigate();
const [email, setEmail] = useState("");
const [password, setPassword] = useState("");

const handleLogin = (e) => {
    e.preventDefault();

    // later connect to backend (Zero Trust IAM core)
    console.log("Admin login:", email, password);

    // TEMP success redirect
    navigate("/admin/dashboard");
};

return (
    <Box
    sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #0f2027, #203a43, #2c5364)"
    }}
    >
    <Paper elevation={10} sx={{ width: 380, p: 4 }}>
        {/* Header */}
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

        {/* Login Form */}
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
            sx={{ mt: 3, py: 1.2 }}
        >
            Login
        </Button>
        </Box>

        {/* Footer */}
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
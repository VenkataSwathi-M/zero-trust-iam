import { Box, Button, Card, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";

export default function SelectLogin() {
const navigate = useNavigate();

return (
    <Box sx={{ minHeight: "100vh", display: "flex", justifyContent: "center", alignItems: "center" }}>
    <Card sx={{ p: 4, width: 360, textAlign: "center" }}>
        <Typography variant="h6" gutterBottom>
        Login As
        </Typography>

        <Button
        fullWidth
        variant="contained"
        sx={{ mt: 2 }}
        onClick={() => navigate("/admin/login")}
        >
        Admin
        </Button>

        <Button
        fullWidth
        variant="outlined"
        sx={{ mt: 2 }}
        onClick={() => navigate("/agent/login")}
        >
        Agent
        </Button>
    </Card>
    </Box>
);
}
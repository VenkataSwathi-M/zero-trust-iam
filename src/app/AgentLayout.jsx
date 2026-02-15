import { useEffect } from "react";
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { Box, AppBar, Toolbar, Typography, Button } from "@mui/material";

export default function AgentLayout() {
const navigate = useNavigate();

useEffect(() => {
const token = localStorage.getItem("token");
if (!token) navigate("/agent/login");
}, [navigate]);

const logout = () => {
    localStorage.removeItem("token");
    navigate("/agent/login");
};

return (
    <Box>
    <AppBar position="static">
        <Toolbar>
        <Typography sx={{ flexGrow: 1 }}>Client Agent Portal</Typography>

        <Button color="inherit" component={NavLink} to="/agent/dashboard">
            Dashboard
        </Button>

        <Button color="inherit" component={NavLink} to="/agent/request">
            Request Access
        </Button>

        <Button color="inherit" onClick={logout}>
            Logout
        </Button>
        </Toolbar>
    </AppBar>

    <Box sx={{ p: 3 }}>
        <Outlet />
    </Box>
    </Box>
);
}
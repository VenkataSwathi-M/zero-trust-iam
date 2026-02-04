import { Outlet, NavLink } from "react-router-dom";
import {
Box,
AppBar,
Toolbar,
Typography,
Button
} from "@mui/material";

export default function AgentLayout() {
return (
    <Box>
    <AppBar position="static">
        <Toolbar>
        <Typography sx={{ flexGrow: 1 }}>
            Client Agent Portal
        </Typography>

        <Button color="inherit" component={NavLink} to="/agent/dashboard">
            Dashboard
        </Button>

        <Button color="inherit" component={NavLink} to="/agent/request">
            Request Access
        </Button>
        </Toolbar>
    </AppBar>

    <Box sx={{ p: 3 }}>
        <Outlet />
    </Box>
    </Box>
);
}
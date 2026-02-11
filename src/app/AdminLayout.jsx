import { Outlet, NavLink } from "react-router-dom";
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Drawer,
  List,
  ListItemButton,
  ListItemText,
} from "@mui/material";

const drawerWidth = 220;

export default function AdminLayout() {
  return (
    <Box sx={{ display: "flex" }}>
      {/* Top Bar */}
      <AppBar position="fixed" sx={{ zIndex: 1201 }}>
        <Toolbar>
          <Typography variant="h6">Zero Trust IAM – Admin</Typography>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          [`& .MuiDrawer-paper`]: {
            width: drawerWidth,
            mt: 8,
          },
        }}
      >
        <List>
          {[
            { label: "Dashboard", path: "/admin/dashboard" },
            { label: "Agents", path: "/admin/agents" },
            { label: "Policies", path: "/admin/policies" },
          ].map((item) => (
            <ListItemButton key={item.path} component={NavLink} to={item.path}>
              <ListItemText primary={item.label} />
            </ListItemButton>
          ))}
        </List>
      </Drawer>

      {/* Content */}
      <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
        <Outlet />
      </Box>
    </Box>
  );
}
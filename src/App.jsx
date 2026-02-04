import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import AdminLayout from "./app/AdminLayout";
import AgentLayout from "./app/AgentLayout";

// Admin pages
import AdminLogin from "./pages/admin/AdminLogin";
import AdminDashboard from "./pages/admin/Dashboard";
import Agents from "./pages/admin/Agents";
import Policies from "./pages/admin/Policies";

// Agent pages
import AgentLogin from "./pages/agent/AgentLogin";
import AgentDashboard from "./pages/agent/AgentDashboard";
import RequestAccess from "./pages/agent/RequestAccess";

export default function App() {
return (
    <BrowserRouter>
<Routes>
        {/* ---------- Admin ---------- */}
        <Route path="/admin/login" element={<AdminLogin />} />

        <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<Navigate to="dashboard" />} />
        <Route path="dashboard" element={<AdminDashboard />} />
        <Route path="agents" element={<Agents />} />
        <Route path="policies" element={<Policies />} />
        </Route>

        {/* ---------- Agent ---------- */}
        <Route path="/agent/login" element={<AgentLogin />} />

        <Route path="/agent" element={<AgentLayout />}>
        <Route index element={<Navigate to="dashboard" />} />
        <Route path="dashboard" element={<AgentDashboard />} />
        <Route path="request" element={<RequestAccess />} />
        </Route>

        {/* Default */}
        <Route path="*" element={<Navigate to="/admin/login" />} />
    </Routes>
    </BrowserRouter>
);
}
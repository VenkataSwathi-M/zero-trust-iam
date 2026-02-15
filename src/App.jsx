import { Routes, Route, Navigate } from "react-router-dom";

import AdminLayout from "./app/AdminLayout";
import AgentLayout from "./app/AgentLayout";
import SelectLogin from "./pages/common/SelectLogin";

// Admin pages
import AdminLogin from "./pages/admin/AdminLogin";
import AdminDashboard from "./pages/admin/Dashboard";
import Agents from "./pages/admin/Agents";
import CreateAgent from "./pages/admin/CreateAgent";
import Policies from "./pages/admin/Policies";
import CreatePolicy from "./pages/admin/CreatePolicy";

// Agent pages
import AgentLogin from "./pages/agent/AgentLogin";
import AgentDashboard from "./pages/agent/AgentDashboard";
import RequestAccess from "./pages/agent/RequestAccess";

// ✅ Banking pages (ONLY ONE set)
import BankingHome from "./pages/banking/BankingHome";
import BankingRead from "./pages/banking/BankingRead";
import BankingTransactions from "./pages/banking/BankingTransactions";
import BankingTransfer from "./pages/banking/BankingTransfer";
import BankingWrite from "./pages/banking/BankingWrite"; // ✅ you will create this

export default function App() {
  return (
    <Routes>
      {/* Default */}
      <Route path="/" element={<Navigate to="/login" />} />

      {/* Login selector */}
      <Route path="/login" element={<SelectLogin />} />

      {/* ----------- ADMIN ----------- */}
      <Route path="/admin/login" element={<AdminLogin />} />
      <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<Navigate to="dashboard" />} />
        <Route path="dashboard" element={<AdminDashboard />} />
        <Route path="agents" element={<Agents />} />
        <Route path="agents/create" element={<CreateAgent />} />
        <Route path="policies" element={<Policies />} />
        <Route path="policies/create" element={<CreatePolicy />} />
      </Route>

      {/* ----------- AGENT ----------- */}
      <Route path="/agent/login" element={<AgentLogin />} />

      <Route path="/agent" element={<AgentLayout />}>
        <Route index element={<Navigate to="dashboard" />} />
        <Route path="dashboard" element={<AgentDashboard />} />
        <Route path="request" element={<RequestAccess />} />

        {/* ✅ BANKING MODULE UNDER AGENT LAYOUT */}
        <Route path="banking" element={<BankingHome />} />
        <Route path="banking/read" element={<BankingRead />} />
        <Route path="banking/write" element={<BankingWrite />} />
        <Route path="banking/transactions" element={<BankingTransactions />} />
        <Route path="banking/transfer" element={<BankingTransfer />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/login" />} />
    </Routes>
  );
}
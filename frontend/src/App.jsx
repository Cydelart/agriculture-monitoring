import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import AdminDashboard from "./pages/AdminDashboard";
import Unauthorized from "./pages/Unauthorized";
import ProtectedRoute from "./auth/ProtectedRoute";
import { getUserRole } from "./auth/auth.js";

export default function App() {
  const role = getUserRole();

  return (
    <BrowserRouter>
      <Routes>

        {/* Public */}
        <Route path="/login" element={<Login />} />

        {/* Farmer + Worker */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute allowedRoles={["farmer"]}>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Admin only */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />

        {/* Unauthorized */}
        <Route path="/unauthorized" element={<Unauthorized />} />

        {/* Default route → redirection automatique selon rôle */}
        <Route
          path="*"
          element={
            <ProtectedRoute allowedRoles={["admin", "farmer", "worker"]}>
              <Navigate
                to={
                  role === "admin"
                    ? "/admin"
                    : role === "farmer" || role === "worker"
                    ? "/dashboard"
                    : "/unauthorized"
                }
                replace
              />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

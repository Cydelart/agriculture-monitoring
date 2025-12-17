import React from "react";
import { Navigate } from "react-router-dom";
import { isAuthenticated, getUserRole } from "./auth.js";

export default function ProtectedRoute({ allowedRoles, children }) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  const role = getUserRole();

  // Redirige selon le rôle si la route n'est pas autorisée
  if (!allowedRoles.includes(role)) {
    // Exemple : si l'utilisateur est admin mais essaie de /dashboard
    if (role === "admin") return <Navigate to="/admin" replace />;
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
}

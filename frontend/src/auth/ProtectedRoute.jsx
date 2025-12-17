// src/components/ProtectedRoute.jsx
import { Navigate } from "react-router-dom";
import { isAuthenticated, getUserRole } from "auth/auth";

/**
 * ProtectedRoute : sécurise une route selon l'authentification et le rôle
 * @param {ReactNode} children - composant à afficher si autorisé
 * @param {Array} roles - liste des rôles autorisés (optionnel)
 */
const ProtectedRoute = ({ children, roles = [] }) => {
  // 1️⃣ Vérifier si l'utilisateur est connecté
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  // 2️⃣ Vérifier le rôle si roles est défini
  const role = getUserRole();
  if (roles.length > 0 && !roles.includes(role)) {
    return <Navigate to="/unauthorized" replace />; // page 403
  }

  // 3️⃣ Si tout va bien, afficher le composant
  return children;
};

export default ProtectedRoute;

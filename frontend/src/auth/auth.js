// auth.js
import * as jwtDecode from "jwt-decode"; // Compatible avec Vite

// Récupère le token d'accès depuis le localStorage
export function getAccessToken() {
  return localStorage.getItem("access_token");
}

// Vérifie si l'utilisateur est authentifié
export function isAuthenticated() {
  return !!getAccessToken();
}

// Récupère le rôle de l'utilisateur depuis le token JWT
export function getUserRole() {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const decoded = jwtDecode.default(token); // ⚠️ .default nécessaire avec import * as
    console.log("Decoded token:", decoded);
    console.log("Role from token:", decoded.role);
    return decoded.role || null; // doit correspondre à "admin", "farmer", "worker"
  } catch (error) {
    console.error("Error decoding token:", error);
    return null;
  }
}

// Déconnecte l'utilisateur
export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

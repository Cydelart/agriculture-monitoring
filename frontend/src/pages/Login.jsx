import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await axios.post(
        "http://localhost:8000/api/token/",
        { username, password }
      );

      localStorage.setItem("access_token", response.data.access);
      localStorage.setItem("refresh_token", response.data.refresh);

      const tokenPayload = JSON.parse(atob(response.data.access.split(".")[1]));
      const role = tokenPayload.role;

      if (role === "admin") navigate("/admin-dashboard");
      else if (role === "farmer") navigate("/farmer-dashboard");
      else navigate("/login");
    } catch {
      setError("Nom d’utilisateur ou mot de passe invalide");
    }
  };

  return (
    <div style={styles.wrapper}>
      <div style={styles.overlay}>
        <div style={styles.card}>
          <h1 style={styles.logo}>🌿 SMARTAGR</h1>
          <p style={styles.subtitle}>Bienvenue! Connectez-vous pour continuer</p>

          {error && <p style={styles.error}>{error}</p>}

          <form onSubmit={handleLogin} style={styles.form}>
            <div style={styles.inputGroup}>
              <label style={styles.label}>Nom d’utilisateur</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Entrez votre nom d’utilisateur"
                style={styles.input}
                required
              />
            </div>

            <div style={styles.inputGroup}>
              <label style={styles.label}>Mot de passe</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Entrez votre mot de passe"
                style={styles.input}
                required
              />
            </div>

            <button type="submit" style={styles.button}>Se connecter</button>
          </form>

          <p style={styles.footer}>🌱 Agriculture Monitoring System</p>
        </div>
      </div>
    </div>
  );
}

const styles = {
  wrapper: {
    minHeight: "100vh",
    width: "100vw",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    backgroundSize: "cover",
    backgroundPosition: "center",
    background: "rgba(179, 218, 171, 0.95)",
    fontFamily: "'Roboto', sans-serif",
  },
  overlay: {
    width: "100%",
    height: "100%",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  card: {
    width: "400px",
    padding: "40px",
    background: "rgba(255,255,255,0.95)",
    borderRadius: "20px",
    boxShadow: "0 15px 35px rgba(0,0,0,0.3)",
    textAlign: "center",
  },
  logo: {
    fontSize: "2.5rem",
    marginBottom: "10px",
    color: "#2f7d32",
    fontWeight: "700",
  },
  subtitle: {
    fontSize: "1rem",
    marginBottom: "25px",
    color: "#555",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "20px",
  },
  inputGroup: {
    display: "flex",
    flexDirection: "column",
    textAlign: "left",
  },
  label: {
    marginBottom: "5px",
    fontWeight: "500",
    color: "#333",
  },
  input: {
    padding: "12px",
    borderRadius: "10px",
    border: "1px solid #ccc",
    fontSize: "14px",
    outline: "none",
    transition: "0.3s",
    backgroundColor: "#f9f9f9",
  },
  button: {
    padding: "12px",
    borderRadius: "10px",
    border: "none",
    backgroundColor: "#2f7d32",
    color: "#fff",
    fontSize: "16px",
    fontWeight: "600",
    cursor: "pointer",
    transition: "0.3s",
  },
  error: {
    color: "red",
    fontWeight: "600",
  },
  footer: {
    marginTop: "20px",
    fontSize: "0.9rem",
    color: "#777",
  },
};

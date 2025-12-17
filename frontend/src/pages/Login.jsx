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

      navigate("/dashboard");
    } catch (err) {
      setError("Invalid username or password");
    }
  };

  return (
    <div style={styles.wrapper}>
      <div style={styles.card}>
        <h2 style={styles.title}>🌱 Agriculture Monitoring</h2>
        <p style={styles.subtitle}>Login to your account</p>

        {error && <p style={styles.error}>{error}</p>}

        <form onSubmit={handleLogin}>
          <div style={styles.field}>
            <label>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              style={styles.input}
            />
          </div>

          <div style={styles.field}>
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={styles.input}
            />
          </div>

          <button type="submit" style={styles.button}>
            Login
          </button>
        </form>
      </div>
    </div>
  );
}

const styles = {
  wrapper: {
    minHeight: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "#f4f7f5",
  },
  card: {
    width: "360px",
    padding: "30px",
    background: "#ffffff",
    borderRadius: "10px",
    boxShadow: "0 10px 25px rgba(0,0,0,0.08)",
  },
  title: {
    textAlign: "center",
    color: "#2f7d32",
    marginBottom: "5px",
  },
  subtitle: {
    textAlign: "center",
    color: "#777",
    marginBottom: "20px",
  },
  field: {
    marginBottom: "15px",
    display: "flex",
    flexDirection: "column",
  },
  input: {
    padding: "10px",
    borderRadius: "6px",
    border: "1px solid #ccc",
    fontSize: "14px",
  },
  button: {
    width: "100%",
    padding: "10px",
    background: "#2f7d32",
    color: "#fff",
    border: "none",
    borderRadius: "6px",
    fontSize: "16px",
    cursor: "pointer",
  },
  error: {
    color: "red",
    textAlign: "center",
    marginBottom: "10px",
  },
};

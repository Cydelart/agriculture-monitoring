import React from "react";

export default function AdminDashboard() {
  return (
    <div style={styles.wrapper}>
      <h1 style={styles.title}>🌿 Admin Dashboard</h1>
      <p style={styles.subtitle}>Welcome to the admin panel!</p>

      <div style={styles.cards}>
        <div style={styles.card}>Users</div>
        <div style={styles.card}>Reports</div>
        <div style={styles.card}>Settings</div>
      </div>
    </div>
  );
}

const styles = {
  wrapper: {
    minHeight: "100vh",
    padding: "40px",
    background: "#f4f7f5",
    fontFamily: "Arial, sans-serif",
  },
  title: {
    color: "#2f7d32",
    textAlign: "center",
    marginBottom: "10px",
  },
  subtitle: {
    textAlign: "center",
    color: "#555",
    marginBottom: "30px",
  },
  cards: {
    display: "flex",
    justifyContent: "center",
    gap: "20px",
  },
  card: {
    padding: "20px",
    background: "#fff",
    borderRadius: "10px",
    boxShadow: "0 5px 15px rgba(0,0,0,0.1)",
    minWidth: "120px",
    textAlign: "center",
    fontWeight: "bold",
    cursor: "pointer",
    transition: "0.2s",
  },
};

import React from "react";

export default function Unauthorized() {
  return (
    <div style={styles.wrapper}>
      <h1 style={styles.title}>❌ Unauthorized</h1>
      <p style={styles.subtitle}>You do not have access to this page.</p>
    </div>
  );
}

const styles = {
  wrapper: {
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    background: "#f4f7f5",
    fontFamily: "Arial, sans-serif",
  },
  title: {
    color: "#d32f2f",
    fontSize: "36px",
    marginBottom: "10px",
  },
  subtitle: {
    fontSize: "18px",
    color: "#555",
  },
};

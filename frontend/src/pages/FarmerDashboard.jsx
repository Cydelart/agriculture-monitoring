// src/components/FarmerDashboard.jsx
import React from "react";

function FarmerDashboard() {
  return (
    <div style={{ padding: "20px" }}>
      <h1>Farmer Dashboard</h1>
      <p>Welcome, Farmer!</p>
      <button onClick={() => {
        localStorage.clear();
        window.location.href = "/login";
      }}>Logout</button>
    </div>
  );
}

export default FarmerDashboard;

import React from "react";

export default function Dashboard() {
  return (
    <div style={{ display: "flex" }}>
      <Sidebar />
      <div style={{ flex: 1, padding: "20px" }}>
        <h1>Dashboard</h1>
        <SensorChart />
        <AnomalyList />
      </div>
    </div>
  );
}

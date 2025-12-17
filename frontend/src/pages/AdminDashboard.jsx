// src/components/AdminDashboard.jsx
import React from "react";

import React, { useEffect, useMemo, useState } from "react";
import { api } from "../../api/api";
import { Link } from "react-router-dom";

function AdminDashboard() {
  return (
    <div style={{ padding: "20px" }}>
      <h1>Admin Dashboard</h1>
      <p>Welcome, Admin!</p>
      <button
        onClick={() => {
          localStorage.clear();
          window.location.href = "/login";
        }}
      >
        Logout
      </button>
    </div>
  );
}

export default AdminDashboard;

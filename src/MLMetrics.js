import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, Cell
} from "recharts";

function MLMetrics() {
  const [metrics, setMetrics] = useState(null);
  const [readings, setReadings] = useState([]);
  const [token, setToken] = useState(null);
  const [anomalyStats, setAnomalyStats] = useState([]);
  const [anomalyCurve, setAnomalyCurve] = useState([]);

  useEffect(() => {
    const USERNAME = "menyar";
    const PASSWORD = "menyar";
    const TOKEN_URL = "http://127.0.0.1:8000/api/token/";

    axios.post(TOKEN_URL, { username: USERNAME, password: PASSWORD })
      .then(res => {
        const accessToken = res.data.access;
        setToken(accessToken);

        axios.get("http://127.0.0.1:8000/api/ml-metrics/", {
          headers: { Authorization: `Bearer ${accessToken}` }
        })
        .then(response => setMetrics(response.data))
        .catch(err => console.error("ML Metrics error:", err));

        axios.get("http://127.0.0.1:8000/api/sensor-readings/", {
          headers: { Authorization: `Bearer ${accessToken}` },
          params: { plot: 1 }
        })

        .then(res => {
          const chartData = res.data.map(r => ({
            timestamp: new Date(r.timestamp).toLocaleTimeString(),
            [r.sensor_type]: r.value
          }));
          setReadings(chartData);
        })
        .catch(err => console.error("Sensor readings error:", err));
        
        axios.get("http://127.0.0.1:8000/api/anomaly-curve/", {
        headers: { Authorization: `Bearer ${accessToken}` }
      })
      .then(res => setAnomalyCurve(res.data))
      .catch(err => console.error("Anomaly curve error:", err));
            })
      .catch(err => console.error("Token fetch error:", err));
  }, []);

  if (!metrics) return <div>Loading ML metrics...</div>;

  const metricData = [
  { name: "Precision", value: metrics.precision * 100 },
  { name: "Recall", value: metrics.recall * 100 },
  { name: "F1-score", value: metrics.f1_score * 100 },
  { name: "False Positive Rate", value: metrics.false_positive_rate * 100 },
  { name: "Total anomalies", value: (metrics.total_anomalies / metrics.total_readings) * 100 },
  { name: "True Positives", value: (metrics.true_positives / metrics.total_readings) * 100 },
];

  const colors = ["#8884d8", "#82ca9d", "#ff7300", "#ff0000", "#00c49f", "#0088FE"];

  // Styles intégrés
  const styles = {
    container: {
      maxWidth: "1200px",
      margin: "0 auto",
      padding: "20px",
      fontFamily: "Arial, sans-serif",
      backgroundColor: "#f5f7fa",
    },
    title: {
      textAlign: "center",
      marginBottom: "30px",
      color: "#333",
    },
    card: {
      backgroundColor: "#fff",
      borderRadius: "12px",
      padding: "20px",
      marginBottom: "30px",
      boxShadow: "0 4px 10px rgba(0,0,0,0.1)",
    },
    sectionTitle: {
      marginBottom: "20px",
      color: "#555",
    },
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>ML Dashboard</h1>

      <div style={styles.card}>
  <h2 style={styles.sectionTitle}>ML Model Metrics</h2>
  <ResponsiveContainer width="100%" height={300}>
    <BarChart
      data={metricData}
      margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
      barSize={40} // largeur des barres
    >
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="name" />
      <YAxis tickFormatter={(value) => `${value.toFixed(1)}%`} />
      <Tooltip formatter={(value) => `${value.toFixed(1)}%`} />
      <Bar dataKey="value" radius={[5, 5, 0, 0]}>
        {metricData.map((entry, index) => (
          <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
        ))}
      </Bar>
    </BarChart>
  </ResponsiveContainer>
</div>

      <div style={styles.card}>
        <h2 style={styles.sectionTitle}>Illustrative Time-series (Last 24h)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={readings} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="moisture" stroke="#8884d8" />
            <Line type="monotone" dataKey="temperature" stroke="#82ca9d" />
            <Line type="monotone" dataKey="humidity" stroke="#ff7300" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div style={styles.card}>
  <h2 style={styles.sectionTitle}>Anomalies Over Time</h2>
  <ResponsiveContainer width="100%" height={300}>
    <LineChart data={anomalyCurve}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="time" />
      <YAxis />
      <Tooltip />
      <Legend />
      <Line
        type="monotone"
        dataKey="count"
        stroke="#ff0000"
        strokeWidth={3}
        dot={{ r: 4 }}
        name="Detected Anomalies"
      />
    </LineChart>
  </ResponsiveContainer>
</div>

    </div>
  );
}

export default MLMetrics;

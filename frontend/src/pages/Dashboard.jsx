import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/axios';
import AdminLayout from '../components/AdminLayout';
import StatusBadge from '../components/StatusBadge';
import {
    FiMapPin,
    FiAlertTriangle,
    FiThermometer,
    FiDroplet,
    FiActivity,
    FiTrendingUp
} from 'react-icons/fi';
import './Dashboard.css';

const Dashboard = () => {
    const [plots, setPlots] = useState([]);
    const [anomalies, setAnomalies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({
        totalPlots: 0,
        criticalPlots: 0,
        totalAnomalies: 0,
        recentAnomalies: 0
    });

    useEffect(() => {
        loadData();
        const interval = setInterval(loadData, 30000); // Refresh every 30 seconds
        return () => clearInterval(interval);
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);

            // Fetch sensor readings to get plot information
            const readingsRes = await api.get('/sensor-readings/');
            const readings = readingsRes.data || [];

            // Fetch anomalies
            const anomaliesRes = await api.get('/anomalies/');
            const allAnomalies = anomaliesRes.data || [];

            // Group readings by plot
            const plotMap = new Map();
            readings.forEach(reading => {
                const plotId = reading.plot || reading.plot_id || reading.field_plot;
                if (!plotId) return;

                if (!plotMap.has(plotId)) {
                    plotMap.set(plotId, {
                        id: plotId,
                        readings: [],
                        anomalyCount: 0,
                        lastReading: null,
                        status: 'normal'
                    });
                }

                const plot = plotMap.get(plotId);
                plot.readings.push(reading);

                // Keep track of the latest reading
                if (!plot.lastReading || new Date(reading.timestamp) > new Date(plot.lastReading.timestamp)) {
                    plot.lastReading = reading;
                }
            });

            // Count anomalies per plot and determine status
            allAnomalies.forEach(anomaly => {
                const plotId = anomaly.plot || anomaly.plot_id || anomaly.field_plot;
                if (plotMap.has(plotId)) {
                    const plot = plotMap.get(plotId);
                    plot.anomalyCount++;

                    // Update status based on severity
                    const severity = anomaly.severity?.toLowerCase();
                    if (severity === 'critical' || severity === 'high') {
                        if (plot.status !== 'critical') {
                            plot.status = 'critical';
                        }
                    } else if (severity === 'warning' || severity === 'medium') {
                        if (plot.status === 'normal') {
                            plot.status = 'warning';
                        }
                    }
                }
            });

            const plotsArray = Array.from(plotMap.values());
            setPlots(plotsArray);
            setAnomalies(allAnomalies.slice(0, 5));

            // Calculate stats
            const criticalCount = plotsArray.filter(p => p.status === 'critical').length;
            const recentAnomaliesCount = allAnomalies.filter(a => {
                const time = new Date(a.timestamp);
                const hourAgo = new Date(Date.now() - 60 * 60 * 1000);
                return time > hourAgo;
            }).length;

            setStats({
                totalPlots: plotsArray.length,
                criticalPlots: criticalCount,
                totalAnomalies: allAnomalies.length,
                recentAnomalies: recentAnomaliesCount
            });

        } catch (error) {
            console.error('Error loading data:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <AdminLayout>
            <div className="dashboard">
                {/* Header */}
                <div className="dashboard-header">
                    <div>
                        <h1>Dashboard</h1>
                        <p className="text-secondary">Monitor your agricultural plots in real-time</p>
                    </div>
                    <button className="btn btn-primary" onClick={loadData}>
                        <FiActivity size={18} />
                        Refresh Data
                    </button>
                </div>

                {/* Stats Grid */}
                <div className="stats-grid">
                    <div className="stat-card">
                        <div className="stat-icon primary">
                            <FiMapPin size={24} />
                        </div>
                        <div className="stat-content">
                            <p className="stat-label">Total Plots</p>
                            <h2 className="stat-value">{loading ? '—' : stats.totalPlots}</h2>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon danger">
                            <FiAlertTriangle size={24} />
                        </div>
                        <div className="stat-content">
                            <p className="stat-label">Critical Plots</p>
                            <h2 className="stat-value">{loading ? '—' : stats.criticalPlots}</h2>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon warning">
                            <FiTrendingUp size={24} />
                        </div>
                        <div className="stat-content">
                            <p className="stat-label">Total Anomalies</p>
                            <h2 className="stat-value">{loading ? '—' : stats.totalAnomalies}</h2>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon success">
                            <FiActivity size={24} />
                        </div>
                        <div className="stat-content">
                            <p className="stat-label">Recent (1h)</p>
                            <h2 className="stat-value">{loading ? '—' : stats.recentAnomalies}</h2>
                        </div>
                    </div>
                </div>

                {/* Main Content Grid */}
                <div className="content-grid">
                    {/* Plots List */}
                    <div className="card plots-section">
                        <div className="card-header">
                            <h3>Agricultural Plots</h3>
                            <span className="badge">{plots.length} Active</span>
                        </div>

                        {loading ? (
                            <div className="loading-state">
                                <div className="spinner"></div>
                                <p>Loading plots...</p>
                            </div>
                        ) : plots.length === 0 ? (
                            <div className="empty-state">
                                <FiMapPin size={48} />
                                <p>No plots found</p>
                                <span>Start monitoring by adding sensor readings</span>
                            </div>
                        ) : (
                            <div className="plots-grid">
                                {plots.map(plot => (
                                    <Link
                                        key={plot.id}
                                        to={`/admin/plots/${plot.id}`}
                                        className="plot-card"
                                    >
                                        <div className="plot-header">
                                            <div className="plot-title">
                                                <FiMapPin size={20} />
                                                <h4>Plot {plot.id}</h4>
                                            </div>
                                            <StatusBadge status={plot.status} />
                                        </div>

                                        {plot.lastReading && (
                                            <div className="plot-metrics">
                                                <div className="metric">
                                                    <FiThermometer size={16} />
                                                    <span>{plot.lastReading.temperature?.toFixed(1)}°C</span>
                                                </div>
                                                <div className="metric">
                                                    <FiDroplet size={16} />
                                                    <span>{plot.lastReading.humidity?.toFixed(1)}%</span>
                                                </div>
                                                <div className="metric">
                                                    <FiDroplet size={16} />
                                                    <span>{plot.lastReading.moisture?.toFixed(1)}%</span>
                                                </div>
                                            </div>
                                        )}

                                        {plot.anomalyCount > 0 && (
                                            <div className="plot-alerts">
                                                <FiAlertTriangle size={14} />
                                                <span>{plot.anomalyCount} anomalies detected</span>
                                            </div>
                                        )}

                                        <div className="plot-footer">
                                            <span className="plot-timestamp">
                                                Last update: {plot.lastReading ?
                                                    new Date(plot.lastReading.timestamp).toLocaleTimeString() :
                                                    'N/A'}
                                            </span>
                                        </div>
                                    </Link>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Recent Alerts */}
                    <div className="card alerts-section">
                        <div className="card-header">
                            <h3>Recent Alerts</h3>
                            <Link to="/admin/alerts" className="view-all-link">
                                View All →
                            </Link>
                        </div>

                        {loading ? (
                            <div className="loading-state">
                                <div className="spinner"></div>
                                <p>Loading alerts...</p>
                            </div>
                        ) : anomalies.length === 0 ? (
                            <div className="empty-state">
                                <FiAlertTriangle size={48} />
                                <p>No recent alerts</p>
                                <span>All systems operating normally</span>
                            </div>
                        ) : (
                            <div className="alerts-list">
                                {anomalies.map(anomaly => (
                                    <div key={anomaly.id} className="alert-item">
                                        <div className="alert-header">
                                            <StatusBadge status={anomaly.severity} />
                                            <span className="alert-time">
                                                {new Date(anomaly.timestamp).toLocaleString()}
                                            </span>
                                        </div>
                                        <div className="alert-content">
                                            <h5>Plot {anomaly.plot || anomaly.plot_id || anomaly.field_plot}</h5>
                                            <p>{anomaly.anomaly_type || 'Anomaly detected'}</p>
                                        </div>
                                        {anomaly.plot && (
                                            <Link
                                                to={`/admin/plots/${anomaly.plot}`}
                                                className="alert-link"
                                            >
                                                View Details →
                                            </Link>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </AdminLayout>
    );
};

export default Dashboard;

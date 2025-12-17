import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api/axios';
import AdminLayout from '../components/AdminLayout';
import StatusBadge from '../components/StatusBadge';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    Area,
    AreaChart
} from 'recharts';
import {
    FiArrowLeft,
    FiThermometer,
    FiDroplet,
    FiAlertTriangle,
    FiActivity,
    FiClock
} from 'react-icons/fi';
import './PlotDetail.css';

const PlotDetail = () => {
    const { plotId } = useParams();
    const [readings, setReadings] = useState([]);
    const [anomalies, setAnomalies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [timeRange, setTimeRange] = useState('24h');

    useEffect(() => {
        loadData();
        const interval = setInterval(loadData, 30000);
        return () => clearInterval(interval);
    }, [plotId, timeRange]);

    const loadData = async () => {
        try {
            setLoading(true);

            // Fetch all sensor readings
            const readingsRes = await api.get('/sensor-readings/');
            const allReadings = readingsRes.data || [];

            // Filter readings for this plot
            const plotReadings = allReadings
                .filter(r => (r.plot || r.plot_id || r.field_plot) == plotId)
                .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

            // Apply time range filter
            const now = new Date();
            const cutoffTime = new Date(
                timeRange === '1h' ? now - 60 * 60 * 1000 :
                    timeRange === '6h' ? now - 6 * 60 * 60 * 1000 :
                        timeRange === '24h' ? now - 24 * 60 * 60 * 1000 :
                            timeRange === '7d' ? now - 7 * 24 * 60 * 60 * 1000 :
                                0
            );

            const filteredReadings = plotReadings.filter(r =>
                new Date(r.timestamp) > cutoffTime
            );

            setReadings(filteredReadings);

            // Fetch anomalies for this plot
            const anomaliesRes = await api.get('/anomalies/');
            const allAnomalies = anomaliesRes.data || [];
            const plotAnomalies = allAnomalies
                .filter(a => (a.plot || a.plot_id || a.field_plot) == plotId)
                .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

            setAnomalies(plotAnomalies);

        } catch (error) {
            console.error('Error loading plot data:', error);
        } finally {
            setLoading(false);
        }
    };

    const formatChartData = () => {
        return readings.map(r => ({
            time: new Date(r.timestamp).toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit'
            }),
            temperature: r.temperature,
            humidity: r.humidity,
            moisture: r.moisture,
            timestamp: r.timestamp
        }));
    };

    const getStats = () => {
        if (readings.length === 0) return null;

        const latest = readings[readings.length - 1];
        const temps = readings.map(r => r.temperature).filter(t => t != null);
        const humidities = readings.map(r => r.humidity).filter(h => h != null);
        const moistures = readings.map(r => r.moisture).filter(m => m != null);

        return {
            current: {
                temperature: latest.temperature,
                humidity: latest.humidity,
                moisture: latest.moisture
            },
            avg: {
                temperature: temps.reduce((a, b) => a + b, 0) / temps.length,
                humidity: humidities.reduce((a, b) => a + b, 0) / humidities.length,
                moisture: moistures.reduce((a, b) => a + b, 0) / moistures.length
            },
            min: {
                temperature: Math.min(...temps),
                humidity: Math.min(...humidities),
                moisture: Math.min(...moistures)
            },
            max: {
                temperature: Math.max(...temps),
                humidity: Math.max(...humidities),
                moisture: Math.max(...moistures)
            }
        };
    };

    const stats = getStats();
    const chartData = formatChartData();

    const CustomTooltip = ({ active, payload }) => {
        if (active && payload && payload.length) {
            return (
                <div className="custom-tooltip">
                    <p className="tooltip-time">{payload[0].payload.time}</p>
                    {payload.map((entry, index) => (
                        <p key={index} style={{ color: entry.color }}>
                            {entry.name}: {entry.value?.toFixed(1)}
                            {entry.name === 'temperature' ? '°C' : '%'}
                        </p>
                    ))}
                </div>
            );
        }
        return null;
    };

    return (
        <AdminLayout>
            <div className="plot-detail">
                {/* Header */}
                <div className="plot-detail-header">
                    <div>
                        <Link to="/admin-dashboard" className="back-link">
                            <FiArrowLeft size={20} />
                            Back to Dashboard
                        </Link>
                        <h1>Plot {plotId}</h1>
                        <p className="text-secondary">Detailed sensor data and anomaly history</p>
                    </div>

                    <div className="header-actions">
                        <div className="time-range-selector">
                            {['1h', '6h', '24h', '7d'].map(range => (
                                <button
                                    key={range}
                                    className={`time-btn ${timeRange === range ? 'active' : ''}`}
                                    onClick={() => setTimeRange(range)}
                                >
                                    {range}
                                </button>
                            ))}
                        </div>
                        <button className="btn btn-primary" onClick={loadData}>
                            <FiActivity size={18} />
                            Refresh
                        </button>
                    </div>
                </div>

                {loading && readings.length === 0 ? (
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Loading plot data...</p>
                    </div>
                ) : readings.length === 0 ? (
                    <div className="empty-state">
                        <FiActivity size={48} />
                        <p>No sensor data available</p>
                        <span>Waiting for sensor readings from this plot</span>
                    </div>
                ) : (
                    <>
                        {/* Current Stats */}
                        {stats && (
                            <div className="current-stats">
                                <div className="stat-card-detail">
                                    <div className="stat-icon-detail temperature">
                                        <FiThermometer size={24} />
                                    </div>
                                    <div className="stat-info">
                                        <p className="stat-label">Temperature</p>
                                        <h2 className="stat-value-detail">
                                            {stats.current.temperature?.toFixed(1)}°C
                                        </h2>
                                        <div className="stat-range">
                                            <span>Min: {stats.min.temperature?.toFixed(1)}°C</span>
                                            <span>Max: {stats.max.temperature?.toFixed(1)}°C</span>
                                            <span>Avg: {stats.avg.temperature?.toFixed(1)}°C</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="stat-card-detail">
                                    <div className="stat-icon-detail humidity">
                                        <FiDroplet size={24} />
                                    </div>
                                    <div className="stat-info">
                                        <p className="stat-label">Humidity</p>
                                        <h2 className="stat-value-detail">
                                            {stats.current.humidity?.toFixed(1)}%
                                        </h2>
                                        <div className="stat-range">
                                            <span>Min: {stats.min.humidity?.toFixed(1)}%</span>
                                            <span>Max: {stats.max.humidity?.toFixed(1)}%</span>
                                            <span>Avg: {stats.avg.humidity?.toFixed(1)}%</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="stat-card-detail">
                                    <div className="stat-icon-detail moisture">
                                        <FiDroplet size={24} />
                                    </div>
                                    <div className="stat-info">
                                        <p className="stat-label">Soil Moisture</p>
                                        <h2 className="stat-value-detail">
                                            {stats.current.moisture?.toFixed(1)}%
                                        </h2>
                                        <div className="stat-range">
                                            <span>Min: {stats.min.moisture?.toFixed(1)}%</span>
                                            <span>Max: {stats.max.moisture?.toFixed(1)}%</span>
                                            <span>Avg: {stats.avg.moisture?.toFixed(1)}%</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Charts */}
                        <div className="charts-section">
                            <div className="card chart-card">
                                <div className="card-header">
                                    <h3>Temperature Over Time</h3>
                                </div>
                                <ResponsiveContainer width="100%" height={300}>
                                    <AreaChart data={chartData}>
                                        <defs>
                                            <linearGradient id="colorTemp" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                                                <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                        <XAxis
                                            dataKey="time"
                                            stroke="#9ca3af"
                                            style={{ fontSize: '0.75rem' }}
                                        />
                                        <YAxis
                                            stroke="#9ca3af"
                                            style={{ fontSize: '0.75rem' }}
                                            label={{ value: '°C', angle: -90, position: 'insideLeft' }}
                                        />
                                        <Tooltip content={<CustomTooltip />} />
                                        <Area
                                            type="monotone"
                                            dataKey="temperature"
                                            stroke="#ef4444"
                                            strokeWidth={2}
                                            fill="url(#colorTemp)"
                                        />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>

                            <div className="card chart-card">
                                <div className="card-header">
                                    <h3>Humidity & Soil Moisture</h3>
                                </div>
                                <ResponsiveContainer width="100%" height={300}>
                                    <LineChart data={chartData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                        <XAxis
                                            dataKey="time"
                                            stroke="#9ca3af"
                                            style={{ fontSize: '0.75rem' }}
                                        />
                                        <YAxis
                                            stroke="#9ca3af"
                                            style={{ fontSize: '0.75rem' }}
                                            label={{ value: '%', angle: -90, position: 'insideLeft' }}
                                        />
                                        <Tooltip content={<CustomTooltip />} />
                                        <Legend />
                                        <Line
                                            type="monotone"
                                            dataKey="humidity"
                                            stroke="#3b82f6"
                                            strokeWidth={2}
                                            dot={false}
                                        />
                                        <Line
                                            type="monotone"
                                            dataKey="moisture"
                                            stroke="#10b981"
                                            strokeWidth={2}
                                            dot={false}
                                        />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Anomaly History */}
                        <div className="card anomaly-history">
                            <div className="card-header">
                                <h3>Anomaly History</h3>
                                <span className="badge">{anomalies.length} Total</span>
                            </div>

                            {anomalies.length === 0 ? (
                                <div className="empty-state">
                                    <FiAlertTriangle size={48} />
                                    <p>No anomalies detected</p>
                                    <span>This plot is operating normally</span>
                                </div>
                            ) : (
                                <div className="anomaly-timeline">
                                    {anomalies.map(anomaly => (
                                        <div key={anomaly.id} className="anomaly-card">
                                            <div className="anomaly-indicator"></div>
                                            <div className="anomaly-content-wrapper">
                                                <div className="anomaly-header">
                                                    <div className="anomaly-title">
                                                        <h4>{anomaly.anomaly_type || 'Anomaly Detected'}</h4>
                                                        <StatusBadge status={anomaly.severity} />
                                                    </div>
                                                    <div className="anomaly-time">
                                                        <FiClock size={14} />
                                                        <span>{new Date(anomaly.timestamp).toLocaleString()}</span>
                                                    </div>
                                                </div>

                                                {anomaly.description && (
                                                    <p className="anomaly-description">{anomaly.description}</p>
                                                )}

                                                {anomaly.agent_recommendation && (
                                                    <div className="agent-recommendation">
                                                        <h5>
                                                            <FiActivity size={16} />
                                                            AI Recommendation
                                                        </h5>
                                                        <p>{anomaly.agent_recommendation}</p>
                                                    </div>
                                                )}

                                                {anomaly.agent_explanation && (
                                                    <div className="agent-explanation">
                                                        <details>
                                                            <summary>View Detailed Explanation</summary>
                                                            <div className="explanation-content">
                                                                <pre>{anomaly.agent_explanation}</pre>
                                                            </div>
                                                        </details>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </>
                )}
            </div>
        </AdminLayout>
    );
};

export default PlotDetail;

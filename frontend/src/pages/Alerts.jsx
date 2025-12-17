import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/axios';
import AdminLayout from '../components/AdminLayout';
import StatusBadge from '../components/StatusBadge';
import {
    FiAlertTriangle,
    FiActivity,
    FiFilter,
    FiClock,
    FiMapPin,
    FiInfo,
    FiCheckCircle
} from 'react-icons/fi';
import './Alerts.css';

const Alerts = () => {
    const [anomalies, setAnomalies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all'); // all, critical, warning, low
    const [sortBy, setSortBy] = useState('newest'); // newest, oldest, severity

    useEffect(() => {
        loadAnomalies();
        const interval = setInterval(loadAnomalies, 30000);
        return () => clearInterval(interval);
    }, []);

    const loadAnomalies = async () => {
        try {
            setLoading(true);
            const response = await api.get('/anomalies/');
            const data = response.data || [];
            setAnomalies(data);
        } catch (error) {
            console.error('Error loading anomalies:', error);
        } finally {
            setLoading(false);
        }
    };

    const getFilteredAndSortedAnomalies = () => {
        let filtered = [...anomalies];

        // Apply filter
        if (filter !== 'all') {
            filtered = filtered.filter(a => {
                const severity = a.severity?.toLowerCase();
                if (filter === 'critical') return severity === 'critical' || severity === 'high';
                if (filter === 'warning') return severity === 'warning' || severity === 'medium';
                if (filter === 'low') return severity === 'low' || severity === 'normal';
                return true;
            });
        }

        // Apply sort
        if (sortBy === 'newest') {
            filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        } else if (sortBy === 'oldest') {
            filtered.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
        } else if (sortBy === 'severity') {
            const severityOrder = { critical: 0, high: 1, warning: 2, medium: 3, low: 4, normal: 5 };
            filtered.sort((a, b) => {
                const aSev = severityOrder[a.severity?.toLowerCase()] ?? 99;
                const bSev = severityOrder[b.severity?.toLowerCase()] ?? 99;
                return aSev - bSev;
            });
        }

        return filtered;
    };

    const filteredAnomalies = getFilteredAndSortedAnomalies();

    const stats = {
        total: anomalies.length,
        critical: anomalies.filter(a => {
            const s = a.severity?.toLowerCase();
            return s === 'critical' || s === 'high';
        }).length,
        warning: anomalies.filter(a => {
            const s = a.severity?.toLowerCase();
            return s === 'warning' || s === 'medium';
        }).length,
        low: anomalies.filter(a => {
            const s = a.severity?.toLowerCase();
            return s === 'low' || s === 'normal';
        }).length
    };

    return (
        <AdminLayout>
            <div className="alerts-page">
                {/* Header */}
                <div className="alerts-header">
                    <div>
                        <h1>Alerts & Anomalies</h1>
                        <p className="text-secondary">
                            Monitor all detected anomalies with AI-powered recommendations
                        </p>
                    </div>
                    <button className="btn btn-primary" onClick={loadAnomalies}>
                        <FiActivity size={18} />
                        Refresh
                    </button>
                </div>

                {/* Stats */}
                <div className="alerts-stats">
                    <div className="alert-stat-card">
                        <div className="alert-stat-icon total">
                            <FiAlertTriangle size={24} />
                        </div>
                        <div className="alert-stat-content">
                            <p className="alert-stat-label">Total Alerts</p>
                            <h2 className="alert-stat-value">{loading ? '—' : stats.total}</h2>
                        </div>
                    </div>

                    <div className="alert-stat-card">
                        <div className="alert-stat-icon critical">
                            <FiAlertTriangle size={24} />
                        </div>
                        <div className="alert-stat-content">
                            <p className="alert-stat-label">Critical</p>
                            <h2 className="alert-stat-value">{loading ? '—' : stats.critical}</h2>
                        </div>
                    </div>

                    <div className="alert-stat-card">
                        <div className="alert-stat-icon warning">
                            <FiAlertTriangle size={24} />
                        </div>
                        <div className="alert-stat-content">
                            <p className="alert-stat-label">Warning</p>
                            <h2 className="alert-stat-value">{loading ? '—' : stats.warning}</h2>
                        </div>
                    </div>

                    <div className="alert-stat-card">
                        <div className="alert-stat-icon low">
                            <FiCheckCircle size={24} />
                        </div>
                        <div className="alert-stat-content">
                            <p className="alert-stat-label">Low Priority</p>
                            <h2 className="alert-stat-value">{loading ? '—' : stats.low}</h2>
                        </div>
                    </div>
                </div>

                {/* Filters */}
                <div className="alerts-controls">
                    <div className="filter-group">
                        <FiFilter size={18} />
                        <span className="filter-label">Filter:</span>
                        <div className="filter-buttons">
                            {['all', 'critical', 'warning', 'low'].map(f => (
                                <button
                                    key={f}
                                    className={`filter-btn ${filter === f ? 'active' : ''}`}
                                    onClick={() => setFilter(f)}
                                >
                                    {f === 'all' ? 'All' : f.charAt(0).toUpperCase() + f.slice(1)}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="sort-group">
                        <span className="sort-label">Sort:</span>
                        <select
                            className="sort-select"
                            value={sortBy}
                            onChange={(e) => setSortBy(e.target.value)}
                        >
                            <option value="newest">Newest First</option>
                            <option value="oldest">Oldest First</option>
                            <option value="severity">By Severity</option>
                        </select>
                    </div>
                </div>

                {/* Alerts List */}
                <div className="card alerts-list-card">
                    {loading && anomalies.length === 0 ? (
                        <div className="loading-state">
                            <div className="spinner"></div>
                            <p>Loading alerts...</p>
                        </div>
                    ) : filteredAnomalies.length === 0 ? (
                        <div className="empty-state">
                            <FiCheckCircle size={64} />
                            <p>No alerts found</p>
                            <span>
                                {filter === 'all'
                                    ? 'No anomalies detected in the system'
                                    : `No ${filter} severity alerts`}
                            </span>
                        </div>
                    ) : (
                        <div className="alerts-list">
                            {filteredAnomalies.map((anomaly, index) => (
                                <div
                                    key={anomaly.id}
                                    className="alert-item-detailed"
                                    style={{ animationDelay: `${index * 50}ms` }}
                                >
                                    <div className="alert-item-header">
                                        <div className="alert-item-left">
                                            <div className="alert-item-icon">
                                                <FiAlertTriangle size={20} />
                                            </div>
                                            <div className="alert-item-title">
                                                <div className="alert-item-top">
                                                    <Link
                                                        to={`/admin/plots/${anomaly.plot || anomaly.plot_id || anomaly.field_plot}`}
                                                        className="plot-link"
                                                    >
                                                        <FiMapPin size={16} />
                                                        Plot {anomaly.plot || anomaly.plot_id || anomaly.field_plot || '?'}
                                                    </Link>
                                                    <StatusBadge status={anomaly.severity} />
                                                </div>
                                                <h3>{anomaly.anomaly_type || 'Anomaly Detected'}</h3>
                                            </div>
                                        </div>
                                        <div className="alert-item-time">
                                            <FiClock size={14} />
                                            <span>{new Date(anomaly.timestamp).toLocaleString()}</span>
                                        </div>
                                    </div>

                                    {anomaly.description && (
                                        <div className="alert-item-description">
                                            <p>{anomaly.description}</p>
                                        </div>
                                    )}

                                    {anomaly.agent_recommendation && (
                                        <div className="alert-recommendation">
                                            <div className="recommendation-header">
                                                <FiActivity size={16} />
                                                <h4>AI Recommendation</h4>
                                            </div>
                                            <p>{anomaly.agent_recommendation}</p>
                                        </div>
                                    )}

                                    {anomaly.agent_explanation && (
                                        <div className="alert-explanation">
                                            <details>
                                                <summary>
                                                    <FiInfo size={14} />
                                                    View Detailed Explanation
                                                </summary>
                                                <div className="explanation-content">
                                                    <pre>{anomaly.agent_explanation}</pre>
                                                </div>
                                            </details>
                                        </div>
                                    )}

                                    <div className="alert-item-footer">
                                        <Link
                                            to={`/admin/plots/${anomaly.plot || anomaly.plot_id || anomaly.field_plot}`}
                                            className="view-plot-btn btn-secondary"
                                        >
                                            <FiMapPin size={16} />
                                            View Plot Details
                                        </Link>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Results Count */}
                {!loading && filteredAnomalies.length > 0 && (
                    <div className="results-info">
                        <p>
                            Showing {filteredAnomalies.length} of {anomalies.length} alerts
                            {filter !== 'all' && ` (filtered by ${filter})`}
                        </p>
                    </div>
                )}
            </div>
        </AdminLayout>
    );
};

export default Alerts;

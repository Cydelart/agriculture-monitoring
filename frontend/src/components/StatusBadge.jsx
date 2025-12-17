import React from 'react';
import './StatusBadge.css';

const StatusBadge = ({ status, count }) => {
    const getStatusClass = () => {
        switch (status?.toLowerCase()) {
            case 'critical':
            case 'high':
                return 'status-critical';
            case 'warning':
            case 'medium':
                return 'status-warning';
            case 'normal':
            case 'low':
            case 'healthy':
                return 'status-normal';
            default:
                return 'status-unknown';
        }
    };

    return (
        <span className={`status-badge ${getStatusClass()}`}>
            {status || 'Unknown'}
            {count !== undefined && <span className="badge-count">{count}</span>}
        </span>
    );
};

export default StatusBadge;

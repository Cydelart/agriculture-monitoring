import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
    FiGrid,
    FiAlertTriangle,
    FiMap,
    FiLogOut,
    FiActivity,
    FiBarChart2
} from 'react-icons/fi';
import './AdminLayout.css';

const AdminLayout = ({ children }) => {
    const location = useLocation();
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.clear();
        navigate('/login');
    };

    const menuItems = [
        { path: '/admin-dashboard', icon: FiGrid, label: 'Dashboard' },
        { path: '/admin/alerts', icon: FiAlertTriangle, label: 'Alerts' },
    ];

    return (
        <div className="admin-layout">
            {/* Sidebar */}
            <aside className="sidebar">
                <div className="sidebar-header">
                    <div className="logo-container">
                        <div className="logo-icon">
                            <FiActivity size={28} />
                        </div>
                        <div className="logo-text">
                            <h2>AgriMonitor</h2>
                            <span>Admin Dashboard</span>
                        </div>
                    </div>
                </div>

                <nav className="sidebar-nav">
                    {menuItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = location.pathname === item.path ||
                            (item.path === '/admin/plots' && location.pathname.startsWith('/admin/plots'));

                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`nav-item ${isActive ? 'active' : ''}`}
                            >
                                <Icon size={20} />
                                <span>{item.label}</span>
                            </Link>
                        );
                    })}
                </nav>

                <div className="sidebar-footer">
                    <button className="logout-btn" onClick={handleLogout}>
                        <FiLogOut size={20} />
                        <span>Logout</span>
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="main-content">
                <div className="content-wrapper">
                    {children}
                </div>
            </main>
        </div>
    );
};

export default AdminLayout;

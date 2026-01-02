import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to log out?')) {
      logout();
      navigate('/login');
    }
  };

  const handleProfile = () => {
    navigate('/profile');
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Dashboard</h1>
        <div className="header-actions">
          <button onClick={handleProfile} className="profile-btn">
            Profile Settings
          </button>
          <button onClick={handleLogout} className="logout-btn">
            Logout
          </button>
        </div>
      </header>

      <div className="dashboard-content">
        <div className="user-info-card">
          <h2>Welcome, {user?.full_name || user?.username}!</h2>
          <div className="user-details">
            {user?.full_name && (
              <div className="detail-row">
                <span className="detail-label">Full Name:</span>
                <span className="detail-value">{user.full_name}</span>
              </div>
            )}
            <div className="detail-row">
              <span className="detail-label">Username:</span>
              <span className="detail-value">{user?.username}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Email:</span>
              <span className="detail-value">{user?.email}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Status:</span>
              <span className={`status-badge ${user?.is_active ? 'active' : 'inactive'}`}>
                {user?.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Role:</span>
              <span className={`role-badge ${user?.is_superuser ? 'admin' : 'user'}`}>
                {user?.is_superuser ? 'Admin' : 'User'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

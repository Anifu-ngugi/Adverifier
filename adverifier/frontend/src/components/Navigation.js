import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

function Navigation() {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navigation">
      <div className="nav-brand">
        <h1>AdVerifier</h1>
      </div>
      <div className="nav-links">
        {user ? (
          <>
            <Link to="/chat">Chat</Link>
            <Link to="/history">History</Link>
            <button onClick={handleLogout} className="logout-btn">Logout</button>
            <span className="user-email">{user.email}</span>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navigation;
import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const PrivateRoute = ({ children }) => {
  const { user, loading } = useContext(AuthContext);

  // Show loading indicator while auth state is being determined
  if (loading) {
    return <div className="loading-container">Loading...</div>;
  }

  // Redirect to login if user is not authenticated
  return user ? children : <Navigate to="/login" replace />;
};

export default PrivateRoute;
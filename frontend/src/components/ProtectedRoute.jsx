import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import AppLoadingScreen from '@/components/ui/AppLoadingScreen';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading, loginDemoUser } = useAuth();
  const location = useLocation();

  // Show loading spinner while checking authentication
  if (loading) {
    return <AppLoadingScreen />;
  }

  // Auto-login demo user for direct access if unauthenticated
  if (!isAuthenticated) {
    if (loginDemoUser) {
      loginDemoUser('admin');
      return children;
    }
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Render protected component
  return children;
};

export default ProtectedRoute;


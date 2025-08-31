import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { LoadingPage } from './ui/loading';

export const ProtectedRoute = ({ children, requiredPermissions = [] }) => {
  const { isAuthenticated, loading, hasPermission } = useAuth();
  const location = useLocation();

  if (loading) {
    return <LoadingPage message="جاري التحقق من الصلاحيات..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check permissions if specified
  if (requiredPermissions.length > 0) {
    const hasRequiredPermissions = requiredPermissions.every(permission =>
      hasPermission(permission)
    );

    if (!hasRequiredPermissions) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-red-600 mb-4">غير مصرح</h2>
            <p className="text-gray-600">ليس لديك صلاحية للوصول إلى هذه الصفحة</p>
          </div>
        </div>
      );
    }
  }

  return children;
};


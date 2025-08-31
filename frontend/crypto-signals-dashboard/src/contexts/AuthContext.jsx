import React, { createContext, useContext, useState, useEffect } from 'react';
import { authUtils } from '../lib/auth';
import { authAPI } from '../lib/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Initialize auth state
  useEffect(() => {
    const initAuth = async () => {
      try {
        const token = authUtils.getToken();
        if (token) {
          // Verify token and get current user
          const isValid = await authUtils.verifyToken();
          if (isValid) {
            const currentUser = await authUtils.getCurrentUser();
            setUser(currentUser);
            setIsAuthenticated(true);
          } else {
            authUtils.removeToken();
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        authUtils.removeToken();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (credentials) => {
    try {
      setLoading(true);
      const result = await authUtils.login(credentials);
      
      if (result.success) {
        setUser(result.user);
        setIsAuthenticated(true);
        return { success: true };
      } else {
        return { success: false, error: result.error };
      }
    } catch (error) {
      return { success: false, error: 'حدث خطأ أثناء تسجيل الدخول' };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authUtils.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const changePassword = async (passwordData) => {
    try {
      const result = await authUtils.changePassword(passwordData);
      return result;
    } catch (error) {
      return { success: false, error: 'حدث خطأ أثناء تغيير كلمة المرور' };
    }
  };

  const hasPermission = (permission) => {
    return authUtils.hasPermission(permission);
  };

  const hasRole = (role) => {
    return authUtils.hasRole(role);
  };

  const hasAnyRole = (roles) => {
    return authUtils.hasAnyRole(roles);
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    logout,
    changePassword,
    hasPermission,
    hasRole,
    hasAnyRole
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};


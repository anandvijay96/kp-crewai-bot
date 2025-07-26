/**
 * Protected Route Component
 * =========================
 * 
 * React component that protects routes requiring authentication.
 * Redirects to login if user is not authenticated or unauthorized.
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  requiredRole?: string;
  requiredPermissions?: string[];
  requireAllPermissions?: boolean;
  fallback?: React.ReactNode;
  redirectTo?: string;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requireAuth = true,
  requiredRole,
  requiredPermissions = [],
  requireAllPermissions = false,
  fallback,
  redirectTo = '/auth/login',
}) => {
  const { 
    isAuthenticated, 
    isLoading, 
    user, 
    hasRole, 
    hasPermission 
  } = useAuth();
  const location = useLocation();

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="protected-route-loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Verifying authentication...</p>
        </div>
      </div>
    );
  }

  // If authentication is required and user is not authenticated
  if (requireAuth && !isAuthenticated) {
    return (
      <Navigate 
        to={redirectTo} 
        state={{ from: location }} 
        replace 
      />
    );
  }

  // If authentication is not required, render children
  if (!requireAuth) {
    return <>{children}</>;
  }

  // Check role-based access
  if (requiredRole && !hasRole(requiredRole)) {
    if (fallback) {
      return <>{fallback}</>;
    }
    
    return (
      <div className="access-denied">
        <div className="access-denied__container">
          <h2 className="access-denied__title">Access Denied</h2>
          <p className="access-denied__message">
            You don't have the required role ({requiredRole}) to access this page.
          </p>
          <div className="access-denied__info">
            <p>Your current role: <strong>{user?.role}</strong></p>
            <p>Required role: <strong>{requiredRole}</strong></p>
          </div>
          <div className="access-denied__actions">
            <button 
              onClick={() => window.history.back()} 
              className="btn btn--secondary"
            >
              Go Back
            </button>
            <Navigate to="/dashboard" />
          </div>
        </div>
      </div>
    );
  }

  // Check permission-based access
  if (requiredPermissions.length > 0) {
    const hasRequiredPermissions = requireAllPermissions
      ? requiredPermissions.every(permission => hasPermission(permission))
      : requiredPermissions.some(permission => hasPermission(permission));

    if (!hasRequiredPermissions) {
      if (fallback) {
        return <>{fallback}</>;
      }

      return (
        <div className="access-denied">
          <div className="access-denied__container">
            <h2 className="access-denied__title">Insufficient Permissions</h2>
            <p className="access-denied__message">
              You don't have the required permissions to access this page.
            </p>
            <div className="access-denied__info">
              <p>Your permissions:</p>
              <ul className="permissions-list">
                {user?.permissions.map((permission, index) => (
                  <li key={index} className="permission-item">
                    {permission}
                  </li>
                ))}
              </ul>
              <p>Required permissions ({requireAllPermissions ? 'all' : 'any'}):</p>
              <ul className="permissions-list">
                {requiredPermissions.map((permission, index) => (
                  <li 
                    key={index} 
                    className={`permission-item ${
                      hasPermission(permission) ? 'permission-item--granted' : 'permission-item--denied'
                    }`}
                  >
                    {permission}
                    {hasPermission(permission) ? ' ✓' : ' ✗'}
                  </li>
                ))}
              </ul>
            </div>
            <div className="access-denied__actions">
              <button 
                onClick={() => window.history.back()} 
                className="btn btn--secondary"
              >
                Go Back
              </button>
              <Navigate to="/dashboard" />
            </div>
          </div>
        </div>
      );
    }
  }

  // All checks passed, render the protected content
  return <>{children}</>;
};

/**
 * Higher-order component for protecting routes
 */
export const withAuth = <P extends object>(
  Component: React.ComponentType<P>,
  options?: Omit<ProtectedRouteProps, 'children'>
) => {
  return (props: P) => (
    <ProtectedRoute {...options}>
      <Component {...props} />
    </ProtectedRoute>
  );
};

/**
 * Hook for conditional rendering based on authentication
 */
export const useProtectedContent = (
  requiredRole?: string,
  requiredPermissions?: string[],
  requireAllPermissions?: boolean
) => {
  const { isAuthenticated, hasRole, hasPermission } = useAuth();

  if (!isAuthenticated) {
    return { canAccess: false, reason: 'not_authenticated' };
  }

  if (requiredRole && !hasRole(requiredRole)) {
    return { canAccess: false, reason: 'insufficient_role' };
  }

  if (requiredPermissions && requiredPermissions.length > 0) {
    const hasRequiredPermissions = requireAllPermissions
      ? requiredPermissions.every(permission => hasPermission(permission))
      : requiredPermissions.some(permission => hasPermission(permission));

    if (!hasRequiredPermissions) {
      return { canAccess: false, reason: 'insufficient_permissions' };
    }
  }

  return { canAccess: true, reason: null };
};

export default ProtectedRoute;

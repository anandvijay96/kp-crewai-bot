/**
 * Authentication Service Hooks
 * ============================
 * 
 * Custom hooks for authentication-related operations.
 * Provides easy-to-use interfaces for login, registration, and user management.
 */

import { useState, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api, ApiError } from '../utils/apiClient';

// Types
interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  full_name: string;
  password: string;
  confirmPassword: string;
  role?: 'user' | 'admin' | 'moderator';
}

interface PasswordResetData {
  email: string;
}

interface PasswordChangeData {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

interface ProfileUpdateData {
  full_name?: string;
  email?: string;
}

interface AuthHookState {
  isLoading: boolean;
  error: string | null;
}

/**
 * Login Hook
 */
export const useLogin = () => {
  const { login } = useAuth();
  const [state, setState] = useState<AuthHookState>({
    isLoading: false,
    error: null,
  });

  const handleLogin = useCallback(async (credentials: LoginCredentials) => {
    setState({ isLoading: true, error: null });
    
    try {
      await login(credentials.email, credentials.password);
    } catch (error) {
      const errorMessage = error instanceof ApiError 
        ? error.message 
        : 'Login failed. Please try again.';
      setState({ isLoading: false, error: errorMessage });
      throw error;
    }
    
    setState({ isLoading: false, error: null });
  }, [login]);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    login: handleLogin,
    clearError,
    ...state,
  };
};

/**
 * Registration Hook
 */
export const useRegister = () => {
  const { register } = useAuth();
  const [state, setState] = useState<AuthHookState>({
    isLoading: false,
    error: null,
  });

  const handleRegister = useCallback(async (userData: RegisterData) => {
    setState({ isLoading: true, error: null });

    // Validate passwords match
    if (userData.password !== userData.confirmPassword) {
      const error = 'Passwords do not match';
      setState({ isLoading: false, error });
      throw new Error(error);
    }

    try {
      const { confirmPassword, ...registrationData } = userData;
      await register(registrationData);
    } catch (error) {
      const errorMessage = error instanceof ApiError 
        ? error.message 
        : 'Registration failed. Please try again.';
      setState({ isLoading: false, error: errorMessage });
      throw error;
    }
    
    setState({ isLoading: false, error: null });
  }, [register]);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    register: handleRegister,
    clearError,
    ...state,
  };
};

/**
 * Password Reset Hook
 */
export const usePasswordReset = () => {
  const [state, setState] = useState<AuthHookState>({
    isLoading: false,
    error: null,
  });

  const requestPasswordReset = useCallback(async (data: PasswordResetData) => {
    setState({ isLoading: true, error: null });
    
    try {
      await api.public('/api/auth/password-reset', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    } catch (error) {
      const errorMessage = error instanceof ApiError 
        ? error.message 
        : 'Password reset request failed. Please try again.';
      setState({ isLoading: false, error: errorMessage });
      throw error;
    }
    
    setState({ isLoading: false, error: null });
  }, []);

  const confirmPasswordReset = useCallback(async (token: string, newPassword: string) => {
    setState({ isLoading: true, error: null });
    
    try {
      await api.public('/api/auth/password-reset/confirm', {
        method: 'POST',
        body: JSON.stringify({ token, new_password: newPassword }),
      });
    } catch (error) {
      const errorMessage = error instanceof ApiError 
        ? error.message 
        : 'Password reset confirmation failed. Please try again.';
      setState({ isLoading: false, error: errorMessage });
      throw error;
    }
    
    setState({ isLoading: false, error: null });
  }, []);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    requestPasswordReset,
    confirmPasswordReset,
    clearError,
    ...state,
  };
};

/**
 * Password Change Hook (for authenticated users)
 */
export const usePasswordChange = () => {
  const [state, setState] = useState<AuthHookState>({
    isLoading: false,
    error: null,
  });

  const changePassword = useCallback(async (data: PasswordChangeData) => {
    setState({ isLoading: true, error: null });

    // Validate new passwords match
    if (data.new_password !== data.confirm_password) {
      const error = 'New passwords do not match';
      setState({ isLoading: false, error });
      throw new Error(error);
    }
    
    try {
      await api.post('/api/auth/change-password', {
        current_password: data.current_password,
        new_password: data.new_password,
      });
    } catch (error) {
      const errorMessage = error instanceof ApiError 
        ? error.message 
        : 'Password change failed. Please try again.';
      setState({ isLoading: false, error: errorMessage });
      throw error;
    }
    
    setState({ isLoading: false, error: null });
  }, []);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    changePassword,
    clearError,
    ...state,
  };
};

/**
 * Profile Management Hook
 */
export const useProfile = () => {
  const { user } = useAuth();
  const [state, setState] = useState<AuthHookState>({
    isLoading: false,
    error: null,
  });

  const updateProfile = useCallback(async (data: ProfileUpdateData) => {
    setState({ isLoading: true, error: null });
    
    try {
      const response = await api.put('/api/auth/profile', data);
      if (response.success) {
        // Update local user data
        const updatedUserData = { ...user, ...data };
        localStorage.setItem('kp_user_data', JSON.stringify(updatedUserData));
        
        // Note: In a real application, you might want to refresh the auth context
        // or trigger a re-fetch of user data
      }
    } catch (error) {
      const errorMessage = error instanceof ApiError 
        ? error.message 
        : 'Profile update failed. Please try again.';
      setState({ isLoading: false, error: errorMessage });
      throw error;
    }
    
    setState({ isLoading: false, error: null });
  }, [user]);

  const refreshProfile = useCallback(async () => {
    setState({ isLoading: true, error: null });
    
    try {
      const response = await api.get('/api/auth/me');
      if (response.success && response.data) {
        localStorage.setItem('kp_user_data', JSON.stringify(response.data));
        return response.data;
      }
    } catch (error) {
      const errorMessage = error instanceof ApiError 
        ? error.message 
        : 'Failed to refresh profile. Please try again.';
      setState({ isLoading: false, error: errorMessage });
      throw error;
    }
    
    setState({ isLoading: false, error: null });
  }, []);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    updateProfile,
    refreshProfile,
    clearError,
    ...state,
  };
};

/**
 * Session Management Hook
 */
export const useSession = () => {
  const { user, tokens, isAuthenticated, logout, refreshToken } = useAuth();
  const [state, setState] = useState<AuthHookState>({
    isLoading: false,
    error: null,
  });

  const validateSession = useCallback(async () => {
    if (!isAuthenticated) return false;
    
    setState({ isLoading: true, error: null });
    
    try {
      const response = await api.get('/api/auth/validate');
      setState({ isLoading: false, error: null });
      return response.success;
    } catch (error) {
      setState({ isLoading: false, error: null });
      return false;
    }
  }, [isAuthenticated]);

  const extendSession = useCallback(async () => {
    setState({ isLoading: true, error: null });
    
    try {
      await refreshToken();
    } catch (error) {
      const errorMessage = error instanceof ApiError 
        ? error.message 
        : 'Session extension failed. Please login again.';
      setState({ isLoading: false, error: errorMessage });
      logout();
      throw error;
    }
    
    setState({ isLoading: false, error: null });
  }, [refreshToken, logout]);

  const getSessionInfo = useCallback(() => {
    if (!tokens) return null;
    
    const tokenExpiry = localStorage.getItem('kp_token_expiry');
    const expiryTime = tokenExpiry ? parseInt(tokenExpiry) : 0;
    const timeUntilExpiry = expiryTime - Date.now();
    
    return {
      isValid: timeUntilExpiry > 0,
      expiresAt: new Date(expiryTime),
      timeUntilExpiry: Math.max(0, timeUntilExpiry),
      shouldRefresh: timeUntilExpiry < 5 * 60 * 1000, // Less than 5 minutes
    };
  }, [tokens]);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    user,
    tokens,
    isAuthenticated,
    validateSession,
    extendSession,
    getSessionInfo,
    logout,
    clearError,
    ...state,
  };
};

/**
 * Permission Management Hook
 */
export const usePermissions = () => {
  const { hasPermission, hasRole, user } = useAuth();

  const checkMultiplePermissions = useCallback((permissions: string[]): boolean => {
    return permissions.every(permission => hasPermission(permission));
  }, [hasPermission]);

  const checkAnyPermission = useCallback((permissions: string[]): boolean => {
    return permissions.some(permission => hasPermission(permission));
  }, [hasPermission]);

  const checkMultipleRoles = useCallback((roles: string[]): boolean => {
    return roles.some(role => hasRole(role));
  }, [hasRole]);

  const getUserPermissions = useCallback(() => {
    return user?.permissions || [];
  }, [user]);

  const isAdmin = useCallback(() => {
    return hasRole('admin');
  }, [hasRole]);

  const isModerator = useCallback(() => {
    return hasRole('moderator') || hasRole('admin'); // Admin has moderator privileges
  }, [hasRole]);

  return {
    hasPermission,
    hasRole,
    checkMultiplePermissions,
    checkAnyPermission,
    checkMultipleRoles,
    getUserPermissions,
    isAdmin,
    isModerator,
    userRole: user?.role,
    permissions: user?.permissions || [],
  };
};

// Export all types
export type {
  LoginCredentials,
  RegisterData,
  PasswordResetData,
  PasswordChangeData,
  ProfileUpdateData,
  AuthHookState,
};

/**
 * Authentication Context Provider
 * ===============================
 * 
 * Manages user authentication state, JWT tokens, and user session.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Types
interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'user' | 'admin' | 'moderator';
  permissions: string[];
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

interface AuthContextType {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  hasPermission: (permission: string) => boolean;
  hasRole: (role: string) => boolean;
}

interface RegisterData {
  email: string;
  full_name: string;
  password: string;
  role?: 'user' | 'admin' | 'moderator';
}


// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Storage keys
const STORAGE_KEYS = {
  ACCESS_TOKEN: 'kp_access_token',
  REFRESH_TOKEN: 'kp_refresh_token',
  USER_DATA: 'kp_user_data',
  TOKEN_EXPIRY: 'kp_token_expiry',
};

// API base URL - Vite uses import.meta.env instead of process.env
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Custom hook to use the auth context
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

/**
 * Authentication Provider Component
 */
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [tokens, setTokens] = useState<AuthTokens | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is authenticated
  const isAuthenticated = !!user && !!tokens;

  /**
   * Initialize auth state from localStorage
   */
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const accessToken = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
        const refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
        const userData = localStorage.getItem(STORAGE_KEYS.USER_DATA);
        const tokenExpiry = localStorage.getItem(STORAGE_KEYS.TOKEN_EXPIRY);

        if (accessToken && refreshToken && userData) {
          const user = JSON.parse(userData);
          const expiryTime = tokenExpiry ? parseInt(tokenExpiry) : 0;
          
          // Check if token is expired
          if (Date.now() < expiryTime) {
            setUser(user);
            setTokens({
              access_token: accessToken,
              refresh_token: refreshToken,
              token_type: 'bearer',
              expires_in: Math.floor((expiryTime - Date.now()) / 1000),
            });
          } else {
            // Try to refresh token
            await refreshTokenSilently(refreshToken);
          }
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error);
        clearAuthData();
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  /**
   * Store auth data in localStorage
   */
  const storeAuthData = (tokens: AuthTokens, user: User) => {
    const expiryTime = Date.now() + (tokens.expires_in * 1000);
    
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, tokens.access_token);
    localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, tokens.refresh_token);
    localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(user));
    localStorage.setItem(STORAGE_KEYS.TOKEN_EXPIRY, expiryTime.toString());
  };

  /**
   * Clear auth data from localStorage
   */
  const clearAuthData = () => {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER_DATA);
    localStorage.removeItem(STORAGE_KEYS.TOKEN_EXPIRY);
    setUser(null);
    setTokens(null);
  };

  /**
   * Make API request with error handling
   */
  const apiRequest = async (url: string, options: RequestInit = {}) => {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || `HTTP error! status: ${response.status}`);
    }

    return data;
  };

  /**
   * Login user with email and password
   */
  const login = async (email: string, password: string): Promise<void> => {
    try {
      setIsLoading(true);
      
      const response = await apiRequest('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });

      if (response.success && response.data) {
        const { access_token, refresh_token, token_type, expires_in, user } = response.data;
        
        const authTokens: AuthTokens = {
          access_token,
          refresh_token,
          token_type,
          expires_in,
        };

        setTokens(authTokens);
        setUser(user);
        storeAuthData(authTokens, user);
      } else {
        throw new Error(response.message || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      clearAuthData();
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Register new user
   */
  const register = async (userData: RegisterData): Promise<void> => {
    try {
      setIsLoading(true);
      
      const response = await apiRequest('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData),
      });

      if (!response.success) {
        throw new Error(response.message || 'Registration failed');
      }

      // After successful registration, user needs to login
      // We don't auto-login for security reasons
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Refresh token silently
   */
  const refreshTokenSilently = async (refreshToken: string): Promise<void> => {
    try {
      const response = await apiRequest('/api/auth/refresh', {
        method: 'POST',
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (response.success && response.data) {
        const { access_token, expires_in } = response.data;
        
        const newTokens: AuthTokens = {
          access_token,
          refresh_token: refreshToken, // Keep existing refresh token
          token_type: 'bearer',
          expires_in,
        };

        setTokens(newTokens);
        
        // Update stored tokens
        const userData = localStorage.getItem(STORAGE_KEYS.USER_DATA);
        if (userData) {
          const user = JSON.parse(userData);
          storeAuthData(newTokens, user);
        }
      } else {
        throw new Error('Token refresh failed');
      }
    } catch (error) {
      console.error('Token refresh error:', error);
      clearAuthData();
      throw error;
    }
  };

  /**
   * Public refresh token method
   */
  const refreshToken = async (): Promise<void> => {
    if (!tokens?.refresh_token) {
      throw new Error('No refresh token available');
    }
    
    await refreshTokenSilently(tokens.refresh_token);
  };

  /**
   * Logout user
   */
  const logout = () => {
    clearAuthData();
    
    // Optional: Call logout endpoint
    if (tokens?.access_token) {
      apiRequest('/api/auth/logout', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${tokens.access_token}`,
        },
      }).catch(error => {
        console.warn('Logout API call failed:', error);
      });
    }
  };

  /**
   * Check if user has specific permission
   */
  const hasPermission = (permission: string): boolean => {
    if (!user) return false;
    return user.permissions.includes(permission) || user.role === 'admin';
  };

  /**
   * Check if user has specific role
   */
  const hasRole = (role: string): boolean => {
    if (!user) return false;
    return user.role === role;
  };

  // Auto-refresh token before expiry
  useEffect(() => {
    if (!tokens) return;

    const refreshInterval = setInterval(() => {
      const expiryTime = localStorage.getItem(STORAGE_KEYS.TOKEN_EXPIRY);
      if (expiryTime) {
        const timeUntilExpiry = parseInt(expiryTime) - Date.now();
        
        // Refresh token 5 minutes before expiry
        if (timeUntilExpiry < 5 * 60 * 1000 && timeUntilExpiry > 0) {
          refreshToken().catch(error => {
            console.error('Auto refresh failed:', error);
            logout();
          });
        }
      }
    }, 60000); // Check every minute

    return () => clearInterval(refreshInterval);
  }, [tokens]);

  const contextValue: AuthContextType = {
    user,
    tokens,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    refreshToken,
    hasPermission,
    hasRole,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

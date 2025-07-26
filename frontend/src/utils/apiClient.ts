/**
 * API Client Utility
 * ==================
 * 
 * Centralized API client for making authenticated HTTP requests to the backend.
 * Handles JWT tokens, automatic token refresh, and request/response interceptors.
 */

// Types
interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
  details?: Record<string, any>;
}

interface RequestConfig extends RequestInit {
  requireAuth?: boolean;
  skipAuthRefresh?: boolean;
}

interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Storage keys (matching AuthContext)
const STORAGE_KEYS = {
  ACCESS_TOKEN: 'kp_access_token',
  REFRESH_TOKEN: 'kp_refresh_token',
  TOKEN_EXPIRY: 'kp_token_expiry',
};

// API configuration - Vite uses import.meta.env instead of process.env
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const DEFAULT_TIMEOUT = 30000; // 30 seconds

/**
 * Custom error class for API errors
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string,
    public details?: Record<string, any>
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * API Client Class
 */
class ApiClient {
  private baseURL: string;
  private timeout: number;

  constructor(baseURL: string = API_BASE_URL, timeout: number = DEFAULT_TIMEOUT) {
    this.baseURL = baseURL;
    this.timeout = timeout;
  }

  /**
   * Get stored access token
   */
  private getAccessToken(): string | null {
    return localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
  }

  /**
   * Get stored refresh token
   */
  private getRefreshToken(): string | null {
    return localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
  }

  /**
   * Check if token is expired
   */
  private isTokenExpired(): boolean {
    const expiryTime = localStorage.getItem(STORAGE_KEYS.TOKEN_EXPIRY);
    if (!expiryTime) return true;
    
    return Date.now() >= parseInt(expiryTime);
  }

  /**
   * Refresh access token
   */
  private async refreshToken(): Promise<void> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      throw new ApiError('No refresh token available', 401, 'NO_REFRESH_TOKEN');
    }

    try {
      const response = await this.makeRequest('/api/auth/refresh', {
        method: 'POST',
        body: JSON.stringify({ refresh_token: refreshToken }),
        skipAuthRefresh: true,
      });

      if (response.success && response.data) {
        const { access_token, expires_in } = response.data;
        const expiryTime = Date.now() + (expires_in * 1000);

        localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, access_token);
        localStorage.setItem(STORAGE_KEYS.TOKEN_EXPIRY, expiryTime.toString());
      } else {
        throw new ApiError('Token refresh failed', 401, 'REFRESH_FAILED');
      }
    } catch (error) {
      // Clear auth data on refresh failure
      localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.TOKEN_EXPIRY);
      localStorage.removeItem('kp_user_data');
      
      throw error;
    }
  }

  /**
   * Create request headers
   */
  private createHeaders(config: RequestConfig = {}): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...config.headers,
    };

    // Add authorization header if required and token is available
    if (config.requireAuth !== false) {
      const token = this.getAccessToken();
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }
    }

    return headers;
  }

  /**
   * Make HTTP request with timeout and error handling
   */
  private async makeRequest<T = any>(
    url: string, 
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const fullUrl = url.startsWith('http') ? url : `${this.baseURL}${url}`;
      
      const response = await fetch(fullUrl, {
        ...config,
        headers: this.createHeaders(config),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const data = await response.json().catch(() => ({ 
        success: false, 
        message: 'Invalid JSON response' 
      }));

      if (!response.ok) {
        throw new ApiError(
          data.message || `HTTP ${response.status}`, 
          response.status,
          data.error,
          data.details
        );
      }

      return data;
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof DOMException && error.name === 'AbortError') {
        throw new ApiError('Request timeout', 408, 'TIMEOUT');
      }

      if (error instanceof ApiError) {
        throw error;
      }

      throw new ApiError(
        error instanceof Error ? error.message : 'Network error',
        0,
        'NETWORK_ERROR'
      );
    }
  }

  /**
   * Make authenticated request with automatic token refresh
   */
  private async authenticatedRequest<T = any>(
    url: string,
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    // Skip auth refresh if explicitly requested
    if (config.skipAuthRefresh) {
      return this.makeRequest<T>(url, config);
    }

    // Check if token needs refresh
    if (this.isTokenExpired()) {
      await this.refreshToken();
    }

    try {
      return await this.makeRequest<T>(url, { ...config, requireAuth: true });
    } catch (error) {
      // Try to refresh token on 401 error
      if (error instanceof ApiError && error.status === 401) {
        try {
          await this.refreshToken();
          return await this.makeRequest<T>(url, { ...config, requireAuth: true });
        } catch (refreshError) {
          // If refresh fails, throw original error
          throw error;
        }
      }
      throw error;
    }
  }

  /**
   * GET request
   */
  async get<T = any>(url: string, config: RequestConfig = {}): Promise<ApiResponse<T>> {
    return this.authenticatedRequest<T>(url, { ...config, method: 'GET' });
  }

  /**
   * POST request
   */
  async post<T = any>(
    url: string, 
    data?: any, 
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    return this.authenticatedRequest<T>(url, {
      ...config,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * PUT request
   */
  async put<T = any>(
    url: string, 
    data?: any, 
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    return this.authenticatedRequest<T>(url, {
      ...config,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * PATCH request
   */
  async patch<T = any>(
    url: string, 
    data?: any, 
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    return this.authenticatedRequest<T>(url, {
      ...config,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * DELETE request
   */
  async delete<T = any>(url: string, config: RequestConfig = {}): Promise<ApiResponse<T>> {
    return this.authenticatedRequest<T>(url, { ...config, method: 'DELETE' });
  }

  /**
   * Upload file (multipart/form-data)
   */
  async upload<T = any>(
    url: string,
    file: File,
    additionalData?: Record<string, string>,
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    const formData = new FormData();
    formData.append('file', file);

    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, value);
      });
    }

    return this.authenticatedRequest<T>(url, {
      ...config,
      method: 'POST',
      headers: {
        // Don't set Content-Type for FormData - browser will set it with boundary
        ...(config.headers && Object.fromEntries(
          Object.entries(config.headers).filter(([key]) => 
            key.toLowerCase() !== 'content-type'
          )
        )),
      },
      body: formData,
    });
  }

  /**
   * Public request (no authentication required)
   */
  async public<T = any>(
    url: string, 
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    return this.makeRequest<T>(url, { ...config, requireAuth: false });
  }
}

// Create singleton instance
const apiClient = new ApiClient();

// Export convenience functions
export const api = {
  get: <T = any>(url: string, config?: RequestConfig) => apiClient.get<T>(url, config),
  post: <T = any>(url: string, data?: any, config?: RequestConfig) =>
    apiClient.post<T>(url, data, config),
  put: <T = any>(url: string, data?: any, config?: RequestConfig) =>
    apiClient.put<T>(url, data, config),
  patch: <T = any>(url: string, data?: any, config?: RequestConfig) =>
    apiClient.patch<T>(url, data, config),
  delete: <T = any>(url: string, config?: RequestConfig) => 
    apiClient.delete<T>(url, config),
  upload: <T = any>(
    url: string,
    file: File,
    additionalData?: Record<string, string>,
    config?: RequestConfig
  ) => apiClient.upload<T>(url, file, additionalData, config),
  public: <T = any>(url: string, config?: RequestConfig) => 
    apiClient.public<T>(url, config),
};

// Export types
export type { ApiResponse, RequestConfig, PaginatedResponse };

// Export client instance for advanced usage
export default apiClient;

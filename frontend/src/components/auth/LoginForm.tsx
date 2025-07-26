/**
 * Login Form Component
 * ====================
 * 
 * React component for user login with form validation and error handling.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useLogin } from '../../hooks/useAuthService';
import { useAuth } from '../../contexts/AuthContext';

interface LoginFormProps {
  onSuccess?: () => void;
  redirectTo?: string;
  showRegisterLink?: boolean;
  className?: string;
}

interface FormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

interface FormErrors {
  email?: string;
  password?: string;
  general?: string;
}

export const LoginForm: React.FC<LoginFormProps> = ({
  onSuccess,
  redirectTo,
  showRegisterLink = true,
  className = '',
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated } = useAuth();
  const { login, isLoading, error, clearError } = useLogin();

  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
    rememberMe: false,
  });

  const [formErrors, setFormErrors] = useState<FormErrors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      const destination = redirectTo || 
        (location.state as any)?.from?.pathname || 
        '/dashboard';
      navigate(destination, { replace: true });
    }
  }, [isAuthenticated, navigate, redirectTo, location.state]);

  // Clear errors when form data changes
  useEffect(() => {
    if (error) {
      clearError();
    }
    setFormErrors({});
  }, [formData, error, clearError]);

  /**
   * Validate form field
   */
  const validateField = (name: keyof FormData, value: string): string | undefined => {
    switch (name) {
      case 'email':
        if (!value.trim()) return 'Email is required';
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          return 'Please enter a valid email address';
        }
        break;
      case 'password':
        if (!value) return 'Password is required';
        if (value.length < 6) return 'Password must be at least 6 characters';
        break;
    }
    return undefined;
  };

  /**
   * Validate entire form
   */
  const validateForm = (): boolean => {
    const errors: FormErrors = {};
    
    errors.email = validateField('email', formData.email);
    errors.password = validateField('password', formData.password);

    setFormErrors(errors);
    return !Object.values(errors).some(error => error);
  };

  /**
   * Handle input change
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    const newValue = type === 'checkbox' ? checked : value;
    
    setFormData(prev => ({
      ...prev,
      [name]: newValue,
    }));

    // Clear field error when user starts typing
    if (formErrors[name as keyof FormErrors]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: undefined,
      }));
    }
  };

  /**
   * Handle input blur
   */
  const handleInputBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setTouched(prev => ({ ...prev, [name]: true }));

    if (touched[name]) {
      const error = validateField(name as keyof FormData, value);
      setFormErrors(prev => ({ ...prev, [name]: error }));
    }
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Mark all fields as touched
    setTouched({
      email: true,
      password: true,
    });

    if (!validateForm()) {
      return;
    }

    try {
      await login({
        email: formData.email.trim(),
        password: formData.password,
      });

      // Success callback
      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      // Error is handled by the useLogin hook
      console.error('Login failed:', err);
    }
  };

  return (
    <div className={`login-form ${className}`}>
      <div className="login-form__container">
        <div className="login-form__header">
          <h2 className="login-form__title">Sign In</h2>
          <p className="login-form__subtitle">
            Welcome back! Please sign in to your account.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="login-form__form" noValidate>
          {/* Email Field */}
          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email Address
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              onBlur={handleInputBlur}
              className={`form-input ${
                formErrors.email ? 'form-input--error' : ''
              }`}
              placeholder="Enter your email address"
              autoComplete="email"
              disabled={isLoading}
              required
            />
            {formErrors.email && (
              <div className="form-error">{formErrors.email}</div>
            )}
          </div>

          {/* Password Field */}
          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              onBlur={handleInputBlur}
              className={`form-input ${
                formErrors.password ? 'form-input--error' : ''
              }`}
              placeholder="Enter your password"
              autoComplete="current-password"
              disabled={isLoading}
              required
            />
            {formErrors.password && (
              <div className="form-error">{formErrors.password}</div>
            )}
          </div>

          {/* Remember Me & Forgot Password */}
          <div className="login-form__options">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="rememberMe"
                checked={formData.rememberMe}
                onChange={handleInputChange}
                disabled={isLoading}
              />
              <span className="checkbox-custom"></span>
              Remember me
            </label>
            
            <Link 
              to="/auth/forgot-password" 
              className="link link--primary"
            >
              Forgot Password?
            </Link>
          </div>

          {/* General Error */}
          {error && (
            <div className="form-error form-error--general">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            className={`btn btn--primary btn--full-width ${
              isLoading ? 'btn--loading' : ''
            }`}
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="btn__spinner"></span>
                Signing In...
              </>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        {/* Register Link */}
        {showRegisterLink && (
          <div className="login-form__footer">
            <p className="text-center">
              Don't have an account?{' '}
              <Link to="/auth/register" className="link link--primary">
                Sign up here
              </Link>
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default LoginForm;

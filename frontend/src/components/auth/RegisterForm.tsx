/**
 * Registration Form Component
 * ==========================
 * 
 * React component for user registration with form validation and error handling.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useRegister } from '../../hooks/useAuthService';
import { useAuth } from '../../contexts/AuthContext';

interface RegisterFormProps {
  onSuccess?: () => void;
  redirectTo?: string;
  showLoginLink?: boolean;
  className?: string;
}

interface FormData {
  email: string;
  full_name: string;
  password: string;
  confirmPassword: string;
  acceptTerms: boolean;
}

interface FormErrors {
  email?: string;
  full_name?: string;
  password?: string;
  confirmPassword?: string;
  acceptTerms?: string;
  general?: string;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({
  onSuccess,
  redirectTo,
  showLoginLink = true,
  className = '',
}) => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { register, isLoading, error, clearError } = useRegister();

  const [formData, setFormData] = useState<FormData>({
    email: '',
    full_name: '',
    password: '',
    confirmPassword: '',
    acceptTerms: false,
  });

  const [formErrors, setFormErrors] = useState<FormErrors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      const destination = redirectTo || '/dashboard';
      navigate(destination, { replace: true });
    }
  }, [isAuthenticated, navigate, redirectTo]);

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
  const validateField = (name: keyof FormData, value: string | boolean): string | undefined => {
    switch (name) {
      case 'email':
        if (!value || typeof value !== 'string') return 'Email is required';
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          return 'Please enter a valid email address';
        }
        break;
      case 'full_name':
        if (!value || typeof value !== 'string') return 'Full name is required';
        if (value.trim().length < 2) return 'Full name must be at least 2 characters';
        break;
      case 'password':
        if (!value || typeof value !== 'string') return 'Password is required';
        if (value.length < 8) return 'Password must be at least 8 characters';
        if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(value)) {
          return 'Password must contain at least one uppercase letter, one lowercase letter, and one number';
        }
        break;
      case 'confirmPassword':
        if (!value || typeof value !== 'string') return 'Please confirm your password';
        if (value !== formData.password) return 'Passwords do not match';
        break;
      case 'acceptTerms':
        if (!value) return 'You must accept the terms and conditions';
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
    errors.full_name = validateField('full_name', formData.full_name);
    errors.password = validateField('password', formData.password);
    errors.confirmPassword = validateField('confirmPassword', formData.confirmPassword);
    errors.acceptTerms = validateField('acceptTerms', formData.acceptTerms);

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
    const { name, value, type, checked } = e.target;
    const fieldValue = type === 'checkbox' ? checked : value;
    setTouched(prev => ({ ...prev, [name]: true }));

    if (touched[name]) {
      const error = validateField(name as keyof FormData, fieldValue);
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
      full_name: true,
      password: true,
      confirmPassword: true,
      acceptTerms: true,
    });

    if (!validateForm()) {
      return;
    }

    try {
      await register({
        email: formData.email.trim(),
        full_name: formData.full_name.trim(),
        password: formData.password,
        confirmPassword: formData.confirmPassword,
        role: 'user', // Default role
      });

      // Success callback
      if (onSuccess) {
        onSuccess();
      } else {
        // Redirect to login page with success message
        navigate('/auth/login', { 
          state: { 
            message: 'Registration successful! Please log in with your credentials.' 
          }
        });
      }
    } catch (err) {
      // Error is handled by the useRegister hook
      console.error('Registration failed:', err);
    }
  };

  return (
    <div className={`register-form ${className}`}>
      <div className="register-form__container">
        <div className="register-form__header">
          <h2 className="register-form__title">Create Account</h2>
          <p className="register-form__subtitle">
            Join KloudPortal SEO Bot and start automating your SEO campaigns.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="register-form__form" noValidate>
          {/* Full Name Field */}
          <div className="form-group">
            <label htmlFor="full_name" className="form-label">
              Full Name
            </label>
            <input
              type="text"
              id="full_name"
              name="full_name"
              value={formData.full_name}
              onChange={handleInputChange}
              onBlur={handleInputBlur}
              className={`form-input ${
                formErrors.full_name ? 'form-input--error' : ''
              }`}
              placeholder="Enter your full name"
              autoComplete="name"
              disabled={isLoading}
              required
            />
            {formErrors.full_name && (
              <div className="form-error">{formErrors.full_name}</div>
            )}
          </div>

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
              placeholder="Create a strong password"
              autoComplete="new-password"
              disabled={isLoading}
              required
            />
            {formErrors.password && (
              <div className="form-error">{formErrors.password}</div>
            )}
            <div className="form-help">
              Password must be at least 8 characters with uppercase, lowercase, and numbers.
            </div>
          </div>

          {/* Confirm Password Field */}
          <div className="form-group">
            <label htmlFor="confirmPassword" className="form-label">
              Confirm Password
            </label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              onBlur={handleInputBlur}
              className={`form-input ${
                formErrors.confirmPassword ? 'form-input--error' : ''
              }`}
              placeholder="Confirm your password"
              autoComplete="new-password"
              disabled={isLoading}
              required
            />
            {formErrors.confirmPassword && (
              <div className="form-error">{formErrors.confirmPassword}</div>
            )}
          </div>

          {/* Terms and Conditions */}
          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="acceptTerms"
                checked={formData.acceptTerms}
                onChange={handleInputChange}
                onBlur={handleInputBlur}
                disabled={isLoading}
                required
              />
              <span className="checkbox-custom"></span>
              I agree to the{' '}
              <Link to="/terms" className="link link--primary" target="_blank">
                Terms of Service
              </Link>{' '}
              and{' '}
              <Link to="/privacy" className="link link--primary" target="_blank">
                Privacy Policy
              </Link>
            </label>
            {formErrors.acceptTerms && (
              <div className="form-error">{formErrors.acceptTerms}</div>
            )}
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
                Creating Account...
              </>
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        {/* Login Link */}
        {showLoginLink && (
          <div className="register-form__footer">
            <p className="text-center">
              Already have an account?{' '}
              <Link to="/auth/login" className="link link--primary">
                Sign in here
              </Link>
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RegisterForm;

/**
 * Login Page Component
 * ====================
 * 
 * Full page wrapper for the login form with proper styling and layout.
 */

import React from 'react';
import { useLocation } from 'react-router-dom';
import { LoginForm } from '../../components/auth/LoginForm';
import { useAuth } from '../../contexts/AuthContext';

export const LoginPage: React.FC = () => {
  const location = useLocation();
  const { isLoading } = useAuth();
  
  // Extract any messages passed from navigation state
  const message = (location.state as any)?.message;
  const from = (location.state as any)?.from;

  return (
    <div className="auth-page">
      <div className="auth-page__container">
        {/* Background decoration */}
        <div className="auth-page__background">
          <div className="auth-bg-pattern"></div>
        </div>

        {/* Main content */}
        <div className="auth-page__content">
          {/* Header section */}
          <div className="auth-page__header">
            <div className="auth-page__logo">
              <h1 className="auth-page__brand">
                <span className="brand-icon">🚀</span>
                KloudPortal SEO Bot
              </h1>
              <p className="auth-page__tagline">
                Automate your SEO campaigns with AI-powered precision
              </p>
            </div>
          </div>

          {/* Success/Info message */}
          {message && (
            <div className="auth-message auth-message--success">
              <div className="auth-message__icon">ℹ️</div>
              <div className="auth-message__content">
                <p>{message}</p>
              </div>
            </div>
          )}

          {/* Redirect notice */}
          {from && (
            <div className="auth-message auth-message--info">
              <div className="auth-message__icon">🔒</div>
              <div className="auth-message__content">
                <p>Please log in to access <strong>{from.pathname}</strong></p>
              </div>
            </div>
          )}

          {/* Login form */}
          <div className="auth-page__form">
            <LoginForm 
              className="auth-form--page"
              showRegisterLink={true}
            />
          </div>

          {/* Features section */}
          <div className="auth-page__features">
            <h3 className="features__title">Why Choose KloudPortal SEO Bot?</h3>
            <div className="features__grid">
              <div className="feature-item">
                <div className="feature-item__icon">🤖</div>
                <h4 className="feature-item__title">AI-Powered Automation</h4>
                <p className="feature-item__description">
                  Leverage advanced AI to discover blogs and generate engaging comments automatically.
                </p>
              </div>
              <div className="feature-item">
                <div className="feature-item__icon">📊</div>
                <h4 className="feature-item__title">Advanced Analytics</h4>
                <p className="feature-item__description">
                  Track your campaign performance with detailed analytics and optimization insights.
                </p>
              </div>
              <div className="feature-item">
                <div className="feature-item__icon">⚡</div>
                <h4 className="feature-item__title">Lightning Fast</h4>
                <p className="feature-item__description">
                  Process hundreds of blogs and generate quality comments in minutes, not hours.
                </p>
              </div>
              <div className="feature-item">
                <div className="feature-item__icon">🛡️</div>
                <h4 className="feature-item__title">Quality Assurance</h4>
                <p className="feature-item__description">
                  Multi-layer validation ensures your comments meet the highest quality standards.
                </p>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="auth-page__footer">
            <p className="footer-text">
              &copy; 2025 KloudPortal SEO Bot. All rights reserved.
            </p>
            <div className="footer-links">
              <a href="/privacy" className="footer-link">Privacy Policy</a>
              <a href="/terms" className="footer-link">Terms of Service</a>
              <a href="/support" className="footer-link">Support</a>
            </div>
          </div>
        </div>

        {/* Loading overlay */}
        {isLoading && (
          <div className="auth-page__loading">
            <div className="loading-overlay">
              <div className="loading-spinner">
                <div className="spinner"></div>
                <p>Signing you in...</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LoginPage;

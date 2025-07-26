/**
 * Registration Page Component
 * ===========================
 * 
 * Full page wrapper for the registration form with proper styling and layout.
 */

import React from 'react';
import { RegisterForm } from '../../components/auth/RegisterForm';
import { useAuth } from '../../contexts/AuthContext';

export const RegisterPage: React.FC = () => {
  const { isLoading } = useAuth();

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
                Join thousands of marketers automating their SEO success
              </p>
            </div>
          </div>

          {/* Registration form */}
          <div className="auth-page__form">
            <RegisterForm 
              className="auth-form--page"
              showLoginLink={true}
            />
          </div>

          {/* Benefits section */}
          <div className="auth-page__features">
            <h3 className="features__title">Start Your SEO Automation Journey</h3>
            <div className="features__grid">
              <div className="feature-item">
                <div className="feature-item__icon">⚡</div>
                <h4 className="feature-item__title">Instant Setup</h4>
                <p className="feature-item__description">
                  Get started in minutes with our intuitive dashboard and automated workflows.
                </p>
              </div>
              <div className="feature-item">
                <div className="feature-item__icon">🎯</div>
                <h4 className="feature-item__title">Targeted Discovery</h4>
                <p className="feature-item__description">
                  Find the most relevant blogs in your niche using advanced AI-powered search.
                </p>
              </div>
              <div className="feature-item">
                <div className="feature-item__icon">📈</div>
                <h4 className="feature-item__title">Scalable Growth</h4>
                <p className="feature-item__description">
                  Scale your outreach efforts without sacrificing quality or authenticity.
                </p>
              </div>
              <div className="feature-item">
                <div className="feature-item__icon">🔒</div>
                <h4 className="feature-item__title">Secure & Compliant</h4>
                <p className="feature-item__description">
                  Enterprise-grade security with full compliance to data protection standards.
                </p>
              </div>
            </div>
          </div>

          {/* Testimonial section */}
          <div className="auth-page__testimonial">
            <div className="testimonial">
              <div className="testimonial__content">
                <blockquote className="testimonial__quote">
                  "KloudPortal SEO Bot has transformed our content marketing strategy. 
                  We've seen a 300% increase in qualified blog engagement within just two months."
                </blockquote>
                <div className="testimonial__author">
                  <div className="author__avatar">👤</div>
                  <div className="author__info">
                    <div className="author__name">Sarah Johnson</div>
                    <div className="author__title">Marketing Director, TechStart Inc.</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Pricing preview */}
          <div className="auth-page__pricing-preview">
            <div className="pricing-preview">
              <h3 className="pricing-preview__title">Choose Your Plan</h3>
              <div className="pricing-preview__plans">
                <div className="pricing-plan pricing-plan--featured">
                  <div className="plan__header">
                    <h4 className="plan__name">Starter</h4>
                    <div className="plan__price">
                      <span className="price__currency">$</span>
                      <span className="price__amount">29</span>
                      <span className="price__period">/month</span>
                    </div>
                  </div>
                  <ul className="plan__features">
                    <li className="feature">✓ 1,000 blog discoveries/month</li>
                    <li className="feature">✓ 500 AI-generated comments</li>
                    <li className="feature">✓ Basic analytics dashboard</li>
                    <li className="feature">✓ Email support</li>
                  </ul>
                </div>
                <div className="pricing-plan pricing-plan--popular">
                  <div className="plan__badge">Most Popular</div>
                  <div className="plan__header">
                    <h4 className="plan__name">Professional</h4>
                    <div className="plan__price">
                      <span className="price__currency">$</span>
                      <span className="price__amount">79</span>
                      <span className="price__period">/month</span>
                    </div>
                  </div>
                  <ul className="plan__features">
                    <li className="feature">✓ 5,000 blog discoveries/month</li>
                    <li className="feature">✓ 2,500 AI-generated comments</li>
                    <li className="feature">✓ Advanced analytics & reports</li>
                    <li className="feature">✓ Priority support</li>
                    <li className="feature">✓ Custom comment templates</li>
                  </ul>
                </div>
                <div className="pricing-plan">
                  <div className="plan__header">
                    <h4 className="plan__name">Enterprise</h4>
                    <div className="plan__price">
                      <span className="price__currency">$</span>
                      <span className="price__amount">199</span>
                      <span className="price__period">/month</span>
                    </div>
                  </div>
                  <ul className="plan__features">
                    <li className="feature">✓ Unlimited blog discoveries</li>
                    <li className="feature">✓ Unlimited AI comments</li>
                    <li className="feature">✓ White-label dashboard</li>
                    <li className="feature">✓ Dedicated account manager</li>
                    <li className="feature">✓ API access</li>
                  </ul>
                </div>
              </div>
              <p className="pricing-preview__note">
                All plans include a 14-day free trial. No credit card required.
              </p>
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
                <p>Creating your account...</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RegisterPage;

import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from '../utils/axios';
import './Login.css';
import logo from '../assets/logo.png';

function Login() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const checkAuth = async () => {
    try {
      const response = await axios.get('/api/v1/auth/check');
      
      if (response.data.authenticated) {
        navigate('/');
      }
    } catch (err) {
      console.error('Auth check failed:', err);
    }
  };
  
  useEffect(() => {
    // Check for error in URL params
    const urlError = searchParams.get('error');
    if (urlError) {
      if (urlError === 'auth_failed') {
        setError('Instagram authentication failed. Please try again.');
      } else {
        setError(`Authentication error: ${urlError}`);
      }
    }
    
    // Check if user is already authenticated
    checkAuth();
  }, [searchParams]);

  const handleInstagramLogin = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Get Instagram auth URL from backend
      const response = await axios.get('/api/v1/auth/instagram');
      
      // Redirect to Instagram OAuth page
      window.location.href = response.data.auth_url;
    } catch (err) {
      setError('Failed to initiate Instagram login. Please try again.');
      console.error('Instagram login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="title-container">
          <img src={logo} alt="Replify Logo" className="login-logo" />
          <h1>Replify AI Assistant</h1>
        </div>
        <p>Login with your Instagram Business account to get started</p>
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
        <button 
          className="instagram-login-button"
          onClick={handleInstagramLogin}
          disabled={loading}
        >
          {loading ? (
            <span>Connecting...</span>
          ) : (
            <>
              <svg className="instagram-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zM5.838 12a6.162 6.162 0 1112.324 0 6.162 6.162 0 01-12.324 0zM12 16a4 4 0 110-8 4 4 0 010 8zm4.965-10.405a1.44 1.44 0 112.881.001 1.44 1.44 0 01-2.881-.001z" fill="currentColor"/>
              </svg>
              Login with Instagram Business
            </>
          )}
        </button>
        
        <p className="login-note">
          Note: You need an Instagram Business or Creator account to use this app
        </p>
      </div>
    </div>
  );
}

export default Login; 
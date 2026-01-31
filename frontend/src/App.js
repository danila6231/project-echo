import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import axios from './utils/axios';
import logo from './assets/logo.png';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(null);
  const [user, setUser] = useState(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      console.log('Checking auth...');
      const response = await axios.get('/api/v1/auth/check');
      console.log('Auth check response:', response.data);
      setIsAuthenticated(response.data.authenticated);
      if (response.data.authenticated) {
        setUser(response.data.user);
      }
    } catch (err) {
      console.error('Auth check failed:', err);
      setIsAuthenticated(false);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post('/api/v1/auth/logout');
      setIsAuthenticated(false);
      setUser(null);
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  // Show loading while checking authentication
  if (isAuthenticated === null) {
    return (
      <div className="App">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="App">
        {isAuthenticated && (
          <header className="App-header">
            <div className="header-content">
              <img src={logo} alt="Replify Logo" className="app-logo" />
              <h1>Replify AI</h1>
            </div>
            <div className="user-info">
              <span>@{user?.username}</span>
              <button className="logout-button" onClick={handleLogout}>
                Logout
              </button>
            </div>
          </header>
        )}
        <main>
          <Routes>
            <Route element={ isAuthenticated ? <Navigate to="/" replace /> : <Login /> } />
            <Route path="/" element={ isAuthenticated ? (<Dashboard />) : (<Navigate to="/login" replace />) }/>
          </Routes>
        </main>
        {isAuthenticated && (
          <footer>
            <p>AI-powered reply suggestions for your Instagram interactions</p>
          </footer>
        )}
      </div>
    </Router>
  );
}

export default App;

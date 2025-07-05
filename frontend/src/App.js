import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import InputScreen from './components/InputScreen';
import OutputScreen from './components/OutputScreen';
import Login from './components/Login';
import axios from './utils/axios';

function App() {
  const [result, setResult] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(null);
  const [user, setUser] = useState(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await axios.get('/api/v1/auth/check');
      
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
            <h1>AI SMM Assistant</h1>
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
            <Route 
              path="/login" 
              element={
                isAuthenticated ? <Navigate to="/" replace /> : <Login />
              } 
            />
            <Route 
              path="/" 
              element={
                isAuthenticated ? (
                  <InputScreen setResult={setResult} />
                ) : (
                  <Navigate to="/login" replace />
                )
              } 
            />
            <Route 
              path="/results/:token" 
              element={
                isAuthenticated ? (
                  <OutputScreen savedResult={result} />
                ) : (
                  <Navigate to="/login" replace />
                )
              } 
            />
          </Routes>
        </main>
        {isAuthenticated && (
          <footer>
            <p>AI-powered content ideas for your social media</p>
          </footer>
        )}
      </div>
    </Router>
  );
}

export default App;

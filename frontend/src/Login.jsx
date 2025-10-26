import React, { useState } from 'react';
import axios from 'axios';
import './Login.css';

const API_URL = 'https://raka-1733-ai-todo-chatbot.hf.space';

function Login({ onLoginSuccess }) {
  const [isSignup, setIsSignup] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Clear form when switching tabs
  const handleTabSwitch = (signup) => {
    setIsSignup(signup);
    setFormData({ username: '', email: '', password: '' }); // CLEAR FORM
    setError('');
  };

  // Email validation function
  const isValidEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(''); // Clear error on input change
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!formData.username.trim()) {
      setError('Username is required');
      return;
    }

    if (formData.username.length < 3) {
      setError('Username must be at least 3 characters');
      return;
    }

    if (isSignup) {
      if (!formData.email.trim()) {
        setError('Email is required');
        return;
      }
      
      if (!isValidEmail(formData.email)) {
        setError('Please enter a valid email address');
        return;
      }
    }

    if (!formData.password) {
      setError('Password is required');
      return;
    }

    if (formData.password.length < 4) {
      setError('Password must be at least 4 characters');
      return;
    }

    setLoading(true);

    try {
      if (isSignup) {
        await axios.post(`${API_URL}/api/signup`, {
          username: formData.username,
          email: formData.email,
          password: formData.password
        });
        
        // After signup, login automatically
        const loginResponse = await axios.post(`${API_URL}/api/login`, {
          username: formData.username,
          password: formData.password
        });
        
        const { token, username } = loginResponse.data;
        localStorage.setItem('token', token);
        localStorage.setItem('username', username);
        onLoginSuccess(token, username);
      } else {
        const response = await axios.post(`${API_URL}/api/login`, {
          username: formData.username,
          password: formData.password
        });
        
        const { token, username } = response.data;
        localStorage.setItem('token', token);
        localStorage.setItem('username', username);
        onLoginSuccess(token, username);
      }
    } catch (err) {
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError(isSignup ? 'Signup failed. Username might already exist.' : 'Invalid credentials');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-header">
          <h1>🤖 AI Todo Assistant</h1>
          <p>Manage your tasks with AI-powered assistance</p>
        </div>

        <div className="login-tabs">
          <button 
            className={!isSignup ? 'active' : ''} 
            onClick={() => handleTabSwitch(false)}
          >
            Login
          </button>
          <button 
            className={isSignup ? 'active' : ''} 
            onClick={() => handleTabSwitch(true)}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              placeholder="Enter username"
              disabled={loading}
            />
          </div>

          {isSignup && (
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="Enter email"
                disabled={loading}
              />
            </div>
          )}

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              placeholder="Enter password"
              disabled={loading}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Please wait...' : (isSignup ? 'Sign Up' : 'Login')}
          </button>
        </form>

        <div className="login-footer">
          {isSignup ? (
            <p>
              Already have an account?{' '}
              <button className="toggle-btn" onClick={() => handleTabSwitch(false)}>
                Login
              </button>
            </p>
          ) : (
            <p>
              Don't have an account?{' '}
              <button className="toggle-btn" onClick={() => handleTabSwitch(true)}>
                Sign Up
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default Login;

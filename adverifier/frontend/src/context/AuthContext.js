import React, { createContext, useState, useEffect } from 'react';

import { api } from '../services/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userId = localStorage.getItem('userId');
    const email = localStorage.getItem('email');

    if (token && userId) {
      setUser({ id: userId, email, token });
      api.defaults.headers.common['Authorization'] = "Token " + token; // ✅ Fixed string interpolation
    }

    setLoading(false);
  }, []);

  const login = async (credentials) => {
    try {
      const response = await api.post('/api/login/', credentials);
      const { token, user_id, email } = response.data;
  
      if (!token || !user_id) {
        throw new Error("Invalid login response: Missing token or user ID");
      }
  
      localStorage.setItem('token', token);
      localStorage.setItem('userId', user_id);
      localStorage.setItem('email', email);
  
      api.defaults.headers.common['Authorization'] = `Token ${token}`;
  
      setUser({ id: user_id, email, token });
  
      console.log("Login Success! User ID stored:", user_id); // ✅ Debugging log
      return { success: true };
    } catch (error) {
      console.error("Login Error:", error.response?.data);
      return {
        success: false,
        message: error.response?.data?.non_field_errors?.[0] || 'Login failed. Check your credentials.'
      };
    }
  };
  
  const register = async (userData) => {
    try {
      const response = await api.post('/api/register/', userData);
      const { token, user_id, email } = response.data;

      localStorage.setItem('token', token);
      localStorage.setItem('userId', user_id);
      localStorage.setItem('email', email);

      api.defaults.headers.common['Authorization'] = "Token " + token; // ✅ Fixed token usage

      setUser({ id: user_id, email, token });
      return { success: true };
    } catch (error) {
      console.error("Registration Error:", error.response?.data);
      return { 
        success: false, 
        message: error.response?.data?.username?.[0] || 
                  error.response?.data?.email?.[0] || 
                  error.response?.data?.password?.[0] || 
                  'Registration failed. Please check your input.' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
    localStorage.removeItem('email');

    delete api.defaults.headers.common['Authorization'];

    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

// ✅ Fixed API Interceptor to correctly retrieve token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    console.log("Token being sent:", token);
    if (token) {
      config.headers.Authorization = "Token " + token;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

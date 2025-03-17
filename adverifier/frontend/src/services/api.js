import axios from 'axios';

export const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// Automatically add Authorization header for each request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token'); // Get token from local storage
  if (token) {
    config.headers.Authorization = `Token ${token}`; // Attach token to request headers
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});



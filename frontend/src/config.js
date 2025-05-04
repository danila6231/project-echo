const isDevelopment = process.env.NODE_ENV === 'development';

export const API_BASE_URL = isDevelopment 
  ? 'http://localhost:8000'  // Development URL
  : 'https://project-echo-5rhk.onrender.com';  // Production URL 
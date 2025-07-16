const isDevelopment = process.env.NODE_ENV === 'development';

export const API_BASE_URL = process.env.API_BASE_URL || (isDevelopment 
  ? 'http://localhost:8000'  // Development URL
  : 'https://project-echo-5rhk.onrender.com');  // Production URL 

export const AUTH_CALLBACK_URL = isDevelopment // NOT USED
  ? 'http://localhost:3000/auth/callback'
  : 'https://your-production-domain.com/auth/callback';  // Update this with your production domain 
# Instagram Business API Setup Guide

This guide will help you set up Instagram Business login for the Replify Assistant.

## Prerequisites

1. A Facebook Developer account
2. An Instagram Business or Creator account
3. The Instagram account must be connected to a Facebook Page

## Step 1: Create a Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click "My Apps" → "Create App"
3. Select "Consumer" as the app type
4. Fill in the app details:
   - App Name: Your app name (e.g., "Replify Assistant")
   - App Contact Email: Your email
   - App Purpose: Select appropriate purpose

## Step 2: Add Instagram Basic Display

1. In your app dashboard, click "Add Product"
2. Find "Instagram Basic Display" and click "Set Up"
3. Click "Create New App" under Instagram Basic Display
4. Fill in the required fields:
   - Display Name: Your app name
   - Valid OAuth Redirect URIs: 
     - For development: `http://localhost:8000/api/v1/auth/instagram/callback`
     - For production: `https://your-domain.com/api/v1/auth/instagram/callback`
   - Deauthorize Callback URL: `https://your-domain.com/api/v1/auth/deauthorize`
   - Data Deletion Request URL: `https://your-domain.com/api/v1/auth/data-deletion`

## Step 3: Get App Credentials

1. In Instagram Basic Display settings, find:
   - Instagram App ID (this is your `INSTAGRAM_CLIENT_ID`)
   - Instagram App Secret (click "Show" and copy - this is your `INSTAGRAM_CLIENT_SECRET`)

## Step 4: Configure Environment Variables

Create a `.env` file in the backend directory with the following:

```env
# Existing variables...

# Instagram App Configuration
INSTAGRAM_CLIENT_ID=your_instagram_app_id_here
INSTAGRAM_CLIENT_SECRET=your_instagram_app_secret_here
INSTAGRAM_REDIRECT_URI=http://localhost:8000/api/v1/auth/instagram/callback

# Session Settings
SESSION_EXPIRY=86400
COOKIE_SECURE=False  # Set to True in production

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

## Step 5: Add Test Users (Development)

1. In Instagram Basic Display → Basic Display → User Token Generator
2. Add Instagram Test Users
3. Click "Generate Token" for testing

## Step 6: Submit for App Review (Production)

For production use, you'll need to submit your app for review:

1. Complete all required fields in App Review
2. Request the following permissions:
   - `instagram_business_basic`
   - `instagram_business_content_publish`
   - `instagram_business_manage_messages`
   - `instagram_business_manage_comments`

## Step 7: Update Frontend Configuration

Update `frontend/src/config.js` with your production domain:

```javascript
export const AUTH_CALLBACK_URL = isDevelopment
  ? 'http://localhost:3000/auth/callback'
  : 'https://your-production-domain.com/auth/callback';
```

## Troubleshooting

### "Invalid OAuth Redirect URI"
- Ensure the redirect URI in your `.env` file matches exactly what's configured in Facebook App settings
- Check for trailing slashes - they must match exactly

### "App Not Active"
- Go to App Dashboard → Settings → Basic
- Toggle "App Mode" to "Live"

### Session/Cookie Issues
- In production, ensure `COOKIE_SECURE=True` in your `.env`
- Make sure your frontend and backend are on the same domain or configure proper CORS

## Testing the Integration

1. Start the backend: `cd backend && uvicorn main:app --reload`
2. Start the frontend: `cd frontend && npm start`
3. Navigate to `http://localhost:3000`
4. Click "Login with Instagram Business"
5. Authorize the app
6. You should be redirected back and logged in

## Security Notes

- Never commit your `.env` file to version control
- Use environment variables in your deployment platform
- Enable HTTPS in production
- Set `COOKIE_SECURE=True` in production
- Regularly rotate your Instagram App Secret 
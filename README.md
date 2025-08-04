# Replify AI Assistant

Generate personalized social media content ideas based on your profile screenshots.

## Overview

Replify AI Assistant helps creators and small businesses generate social media content ideas. Upload 1-3 screenshots of your Instagram (or other social profile) and optionally describe your account. The system analyzes the content and suggests personalized content ideas using an LLM with image understanding.

## Features

- Upload 1-3 screenshots of your social media profile
- Add optional text description of your account (tone, niche, goals)
- Get a brief summary of your account style
- Receive 2-3 content ideas with:
  - Caption drafts
  - Hashtag suggestions
  - Post themes
- No login required
- Bookmark results for later reference

## Tech Stack

- **Frontend**: ReactJS
- **Backend**: FastAPI (Python)
- **LLM**: GPT-4o (multimodal)
- **Database**: Redis (for token-based storage)

## Project Structure

```
project-echo/
├── backend/             # FastAPI Backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Configuration
│   │   ├── models/      # Pydantic models
│   │   ├── redis/       # Redis client
│   │   ├── services/    # Business logic
│   │   └── utils/       # Utility functions
│   ├── main.py          # Application entry point
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile       # Backend Docker config
└── frontend/            # React Frontend
    ├── public/          # Static files
    ├── src/             # React source code
    │   ├── components/  # React components
    │   ├── App.js       # Main App component
    │   └── index.js     # Entry point
    ├── package.json     # NPM dependencies
    └── Dockerfile       # Frontend Docker config
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Redis server

### Backend Setup

1. Create and activate a virtual environment:
   ```
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file (copy from `.env.example`) and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

4. Run the server:
   ```
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Install dependencies:
   ```
   cd frontend
   npm install
   ```

2. Run the development server:
   ```
   npm start
   ```

3. Open http://localhost:3000 in your browser

## Deployment

The application can be deployed using Docker and Docker Compose for both the frontend and backend.

## License

MIT

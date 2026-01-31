# Replify AI Assistant

Generate automatic AI replies that replicate the voice of the author based on your profile screenshots.

## Overview

Replify AI Assistant helps creators and small businesses generate automatic AI replies that replicate the voice of the author. Connect your Instagram business account and the tool will analyze the content and generate replies that mimic the author's voice using an LLM with image understanding.

## Features

- Connect your Instagram profile
- Receive generated replies for incoming comments / messages that replicate your voice

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
   ```shell
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```shell
   pip install -r requirements.txt
   ```

3. Create a `.env` file (copy from `.env.example`) and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

4. Run the server:
   ```shell
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Install dependencies:
   ```shell
   cd frontend
   npm install
   ```

2. Run the development server:
   ```shell
   npm start
   ```

3. Open http://localhost:3000 in your browser

## Deployment

The application can be deployed using Docker and Docker Compose for both the frontend and backend.

(1) Deploying via Docker:
```shell
docker compose down && docker compose up -d --build
```

(2) Deploying via Docker (**hot reload**):
```shell
docker compose watch
```

## License

MIT

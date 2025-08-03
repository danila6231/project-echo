from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI SMM Assistant",
    description="Generate social media content ideas based on profile screenshots"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://project-echo-stage.vercel.app",  # stage frontend
        "https://project-echo-inky.vercel.app", # Production frontend
        "https://replify.to", # Production frontend
        "https://www.replify.to", # Production frontend
        "https://stage.replify.to" # stage frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include API routes
from app.api.v1.endpoints import router as api_router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "this shit is working"} 

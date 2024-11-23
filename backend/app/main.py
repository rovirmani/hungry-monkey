from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.base import router as base_router

app = FastAPI(title="FastAPI + React App")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(base_router, prefix="/api")

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "FastAPI is running!"}

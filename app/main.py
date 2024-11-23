from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .routers import restaurants, vapi

# Load environment variables
load_dotenv()

app = FastAPI(title="Restaurant Holiday Hours API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(restaurants.router, prefix="/api/restaurants", tags=["restaurants"])
app.include_router(vapi.router, prefix="/api/vapi", tags=["vapi"])

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

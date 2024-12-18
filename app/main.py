import asyncio
import logging
import os
import time

from app.middleware.auth import ClerkAuthMiddleware
from fastapi import BackgroundTasks, Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from .clients.vapi import VAPIClient
from .db.restaurants import RestaurantDB
from .routers import restaurants, users, vapi
from .utils.constants import RESTAURANT_CALL_DELAY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Restaurant Holiday Hours API",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

auth = ClerkAuthMiddleware()
vapi_client = VAPIClient()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Status: {response.status_code} Duration: {duration:.2f}s"
    )
    return response

origins = [
    "http://localhost:5173",  # React dev server
    "http://localhost:8000",  # Local development server
    "https://hungry-monkey-nine.vercel.app",  # Vercel production
    "http://hungry-monkey-nine.vercel.app"  # Alternate Vercel domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(restaurants.router, prefix="/api/restaurants", tags=["restaurants"])
app.include_router(vapi.router, prefix="/api/vapi", tags=["vapi"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    logger.info("Backgroung - Starting call dispatch loop")
    asyncio.create_task(vapi_client.call_dispatch_loop())


# Create a handler for Vercel serverless deployment
# Note: We need to use mangum to wrap our FastAPI app
handler = Mangum(app, lifespan="off")

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

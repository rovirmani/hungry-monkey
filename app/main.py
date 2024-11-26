from fastapi import FastAPI, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import asyncio
import logging
import os
import time
from .routers import restaurants, vapi
from .db.restaurants import RestaurantDB
from .clients.vapi import VAPIClient
from app.middleware.auth import ClerkAuthMiddleware

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Restaurant Holiday Hours API")
auth = ClerkAuthMiddleware()

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request details
    logger.info(f" Request: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    try:
        # Get request body if it exists
        body = await request.body()
        if body:
            logger.info(f"Body: {body.decode()}")
    except Exception as e:
        logger.error(f"Error reading body: {e}")
    
    # Process request
    try:
        response = await call_next(request)
        
        # Log response details
        process_time = time.time() - start_time
        logger.info(f" Response: {response.status_code} (took {process_time:.2f}s)")
        
        return response
    except Exception as e:
        logger.error(f" Error processing request: {str(e)}")
        raise

# Configure CORS
origins = [
    "http://localhost:5173",  # React dev server
    "https://hungry-monkey-nine.vercel.app",  # Vercel production
    os.getenv("FRONTEND_URL", ""),  # From environment variable
]

logger.info(f" Configured CORS origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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

@app.get("/api/user/profile")
async def get_user_profile(token: str = Depends(auth)):
    return {"message": "This is a protected route", "token": token}

async def call_dispatch_loop():
    while True:
        try:
            logger.info("Starting call dispatch loop...")
            await dispatch_calls()
        except Exception as e:
            logger.error(f"Error in call dispatch loop: {e}")
        await asyncio.sleep(60)  # Wait 1 minute before next iteration

async def dispatch_calls():
    call_queue = asyncio.Queue()
    # populate the queue with 5 oldest restaurants that haven't been checked
    restaurants_without_hours = RestaurantDB().get_restaurants_without_hours()
    for restaurant in restaurants_without_hours:
        await call_queue.put(restaurant)
    logger.info(f"Populated call queue with {len(restaurants_without_hours)} restaurants")
    
    while not call_queue.empty():
        restaurant = await call_queue.get()
        logger.info(f"Pretending to call 'check-hours' for restaurant: {restaurant['name']}")
        await asyncio.sleep(60 * 5)  # pretend to wait 5 minutes

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    asyncio.create_task(call_dispatch_loop())

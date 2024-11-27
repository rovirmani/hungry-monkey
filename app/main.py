<<<<<<< HEAD
from fastapi import FastAPI, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .routers import restaurants, vapi
import asyncio
import logging
=======
from fastapi import FastAPI, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import asyncio
import logging
import os
import time
from .routers import restaurants, vapi
>>>>>>> origin
from .db.restaurants import RestaurantDB
from .clients.vapi import VAPIClient
from app.middleware.auth import ClerkAuthMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)

<<<<<<< HEAD
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Restaurant Holiday Hours API")
auth = ClerkAuthMiddleware()
=======
app = FastAPI(
    title="Restaurant Holiday Hours API",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

auth = ClerkAuthMiddleware()

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
>>>>>>> origin

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

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

<<<<<<< HEAD
@app.get("/api/user/profile")
async def get_user_profile(token: str = Depends(auth)):
    return {"message": "This is a protected route", "token": token}
=======
@app.get("/api/me")
async def get_user_profile(token: str = Depends(auth)):
    return {"token": token}
>>>>>>> origin

async def call_dispatch_loop():
    while True:
        try:
<<<<<<< HEAD
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
=======
            await dispatch_calls()
        except Exception as e:
            logger.error(f"Error in dispatch loop: {str(e)}")
        await asyncio.sleep(60)  # Wait for 60 seconds before next dispatch

async def dispatch_calls():
    try:
        db = RestaurantDB()
        restaurants = db.get_restaurants_without_hours()
        
        if not restaurants:
            return
            
        vapi_client = VAPIClient()
        for restaurant in restaurants:
            try:
                await vapi_client.get_restaurant_hours(restaurant["business_id"])
            except Exception as e:
                logger.error(f"Failed to get hours for {restaurant['business_id']}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Failed to dispatch calls: {str(e)}")

@app.on_event("startup")
async def startup_event():
    background_tasks = BackgroundTasks()
    background_tasks.add_task(call_dispatch_loop)

# Create a handler for Vercel serverless deployment
# Note: We need to use mangum to wrap our FastAPI app
handler = Mangum(app, lifespan="off")

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
>>>>>>> origin

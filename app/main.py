from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .routers import restaurants, vapi
import asyncio
import logging
from .db.restaurants import RestaurantDB

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

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    asyncio.create_task(call_dispatch_loop())

async def restaurant_check_hours_loop():
    logger.info("Starting call dispatch loop...")
    call_queue = asyncio.Queue()
    # populate the queue with 5 oldest restaurants that haven't been checked
    restaurants_without_hours = RestaurantDB().get_restaurants_without_hours()
    for restaurant in restaurants_without_hours:
        await call_queue.put(restaurant)
    logger.info(f"🚀 Populated call queue with {len(restaurants_without_hours)} restaurants")
    while not call_queue.empty():
        restaurant = await call_queue.get()
        logger.info(f"Pretending to call 'check-hours' for restaurant: {restaurant['name']}")
        await asyncio.sleep(60 * 5)  # pretend to wait 5 minutes

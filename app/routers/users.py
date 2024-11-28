from fastapi import APIRouter, Depends, HTTPException
from ..auth.clerk import require_auth, UserData
from ..db.users import UserDB
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["users"])  # Remove prefix, it's handled in main.py
db = UserDB()

@router.post("/initialize")
async def initialize_user(user: UserData = require_auth):
    """
    Initialize or update a user in our database when they sign in through Clerk.
    """
    try:
        logger.info(f"👤 Initializing user: {user.first_name} {user.last_name}")
        
        # Convert Clerk user data to our format
        user_data = {
            "user_id": user.user_id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_premium": False  # Default to non-premium
        }
        
        # Check if user exists
        existing_user = await db.get_user(user.user_id)
        
        # Create/update user
        success = await db.create_user(user_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to initialize user")
            
        return {
            "status": "updated" if existing_user else "created",
            "message": "User initialized successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to initialize user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
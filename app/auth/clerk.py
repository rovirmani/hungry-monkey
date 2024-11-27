from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import os
import logging
from clerk_backend_api import Clerk, models
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up security
security = HTTPBearer()

# Get Clerk environment variables
clerk_secret_key = os.getenv("CLERK_SECRET_KEY")
print("Clerk secret key:", clerk_secret_key)
if not clerk_secret_key:
    raise ValueError("CLERK_SECRET_KEY not found in environment variables")

# Initialize Clerk client
clerk = Clerk(
    bearer_auth=clerk_secret_key
)

async def verify_auth_token(token: str) -> Optional[dict]:
    """Verify a JWT token from Clerk."""
    try:
        # Verify the token using Clerk's SDK
        response = clerk.jwt.verify(
            token=token
        )
        
        if response is None:
            logger.error("❌ Token verification failed: No response from Clerk")
            return None
            
        logger.info("✅ Token verified successfully")
        return response.to_dict()
        
    except models.ClerkErrors as e:
        logger.error(f"❌ Clerk error: {e.data}")
        return None
    except models.SDKError as e:
        logger.error(f"❌ SDK error: {e.message}")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependency that verifies the auth token and returns the user data."""
    user_data = await verify_auth_token(credentials.credentials)
    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    return user_data

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[dict]:
    """Optional authentication that returns None for unauthenticated users."""
    if not credentials:
        return None
    return await verify_auth_token(credentials.credentials)

# Export the dependencies to use in routes
require_auth = Depends(get_current_user)
optional_auth = Depends(get_optional_user)

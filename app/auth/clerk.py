from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import os
import logging
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up security
security = HTTPBearer()

# Get Clerk environment variables
clerk_secret_key = os.getenv("CLERK_SECRET_KEY")
if not clerk_secret_key:
    raise ValueError("CLERK_SECRET_KEY not found in environment variables")

async def verify_auth_token(token: str) -> Optional[dict]:
    """Verify a JWT token from Clerk."""
    try:
        # Get the token parts
        decoded_token = token.split('.')
        if len(decoded_token) != 3:
            logger.error("❌ Token verification failed: Invalid token format")
            logger.error(f"Token parts: {len(decoded_token)}")
            return None
            
        import json
        import base64
        
        # Decode and log the payload
        try:
            # Log the raw token parts for debugging
            logger.info("🔍 Token structure:")
            logger.info(f"Header: {decoded_token[0]}")
            logger.info(f"Payload (encoded): {decoded_token[1]}")
            
            # Decode the payload
            padded = decoded_token[1] + "=" * ((4 - len(decoded_token[1]) % 4) % 4)
            decoded_bytes = base64.b64decode(padded)
            payload = json.loads(decoded_bytes.decode('utf-8'))
            
            logger.info("🔍 Decoded payload:")
            logger.info(json.dumps(payload, indent=2))
            
            # Get user ID and session ID from the claims
            user_id = payload.get('sub')
            session_id = payload.get('sid')
            
            if not user_id or not session_id:
                logger.error("❌ Token verification failed: Missing user ID or session ID")
                logger.error("Available payload keys: " + ", ".join(payload.keys()))
                return None
            
            # Make direct HTTP request to Clerk API to get user details
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {clerk_secret_key}"}
                user_response = await client.get(
                    f"https://api.clerk.com/v1/users/{user_id}",
                    headers=headers
                )
                
                if user_response.status_code != 200:
                    logger.error(f"❌ Failed to get user details: {user_response.text}")
                    return None
                    
                user_data = user_response.json()
                
                # Get session details
                session_response = await client.get(
                    f"https://api.clerk.com/v1/sessions/{session_id}",
                    headers=headers
                )
                
                if session_response.status_code != 200:
                    logger.error(f"❌ Failed to get session details: {session_response.text}")
                    return None
                    
                session_data = session_response.json()
                
                if session_data.get('status') != 'active':
                    logger.error("❌ Session is not active")
                    return None
                
                logger.info("✅ Token verified successfully")
                return {
                    "session_id": session_id,
                    "user_id": user_id,
                    "email": user_data.get('email_addresses', [{}])[0].get('email_address'),
                    "first_name": user_data.get('first_name'),
                    "last_name": user_data.get('last_name')
                }
                
        except Exception as e:
            logger.error(f"❌ Error processing token: {str(e)}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Unexpected error during authentication: {str(e)}")
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[dict]:
    """Get the current authenticated user from the token."""
    user_data = await verify_auth_token(credentials.credentials)
    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    return user_data

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[dict]:
    """Get the current user if authenticated, otherwise return None."""
    if not credentials:
        return None
    try:
        return await verify_auth_token(credentials.credentials)
    except HTTPException:
        return None

# Export the dependencies to use in routes
require_auth = Depends(get_current_user)
optional_auth = Depends(get_optional_user)

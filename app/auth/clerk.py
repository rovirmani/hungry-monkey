from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt as PyJWT
import json
import httpx
import logging
from typing import Optional
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up security
security = HTTPBearer()

async def get_jwks() -> dict:
    """Get the JWKS from Clerk"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{os.getenv('CLERK_JWT_ISSUER')}/.well-known/jwks.json"
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error("Failed to get JWKS: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to get JWKS")

async def verify_auth_token(token: str) -> Optional[dict]:
    """Verify a JWT token from Clerk."""
    try:
        print(f"Raw token: {token[:20]}...")
        
        # Get unverified header first
        header = PyJWT.get_unverified_header(token)
        if not header or "kid" not in header:
            print(" Invalid token header")
            return None
            
        # Get JWKS
        jwks = await get_jwks()
        if not jwks:
            print(" Failed to get JWKS")
            return None
            
        # Find the key used to sign
        key = next((k for k in jwks["keys"] if k["kid"] == header["kid"]), None)
        if not key:
            print(" No matching key found")
            return None
            
        # Construct the public key
        public_key = PyJWT.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
        
        # Verify and decode with template claims
        decoded = PyJWT.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=os.getenv("CLERK_JWT_AUDIENCE"),
            issuer=os.getenv("CLERK_JWT_ISSUER")
        )
        
        # Verify required template claims
        if not decoded.get("sub"):
            print(" Missing required claim: sub")
            return None
            
        if not decoded.get("azp"):
            print(" Missing required claim: azp")
            return None
        
        return decoded
        
    except Exception as e:
        print(f" Error verifying token: {str(e)}")
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependency that verifies the auth token and returns the user data"""
    token = credentials.credentials
    return await verify_auth_token(token)

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[dict]:
    """Optional authentication that returns None for unauthenticated users"""
    if not credentials:
        return None
    try:
        token = credentials.credentials
        return await verify_auth_token(token)
    except HTTPException:
        return None

# Export the dependencies to use in routes
require_auth = Depends(get_current_user)
optional_auth = Depends(get_optional_user)

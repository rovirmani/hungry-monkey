from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, jwk
import os
from dotenv import load_dotenv
import httpx
from functools import lru_cache
import logging
import json
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

security = HTTPBearer()

def get_jwt_issuer():
    issuer = os.getenv("CLERK_JWT_ISSUER")
    if not issuer:
        raise HTTPException(status_code=500, detail="JWT issuer not configured")
    return issuer

@lru_cache()
async def get_jwks():
    """
    Fetch and cache the JWKS from Clerk
    """
    issuer = get_jwt_issuer()
    jwks_url = f"{issuer}/.well-known/jwks.json"
    logger.info(f"Fetching JWKS from: {jwks_url}")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(jwks_url)
        if response.status_code != 200:
            logger.error(f"Failed to fetch JWKS: {response.text}")
            raise HTTPException(status_code=500, detail="Failed to fetch JWKS")
        return response.json()

async def get_signing_key(kid):
    """
    Get the signing key from JWKS that matches the kid
    """
    jwks = await get_jwks()
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key
    raise HTTPException(status_code=401, detail="Unable to find appropriate key")

async def get_auth_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verify the JWT token from Clerk
    """
    try:
        token = credentials.credentials
        logger.info("Raw token: %s", token)
        
        # First decode without verification to get claims and headers
        try:
            unverified_headers = jwt.get_unverified_headers(token)
            logger.info("Unverified headers: %s", json.dumps(unverified_headers, indent=2))
            unverified_claims = jwt.get_unverified_claims(token)
            logger.info("Unverified claims: %s", json.dumps(unverified_claims, indent=2))
        except Exception as e:
            logger.error("Failed to decode token: %s", str(e))
            raise HTTPException(status_code=401, detail=f"Failed to decode token: {str(e)}")
        
        # Get and verify issuer
        issuer = get_jwt_issuer()
        logger.info("Expected issuer: %s", issuer)
        logger.info("Token issuer: %s", unverified_claims.get('iss'))
        
        if unverified_claims.get('iss') != issuer:
            logger.error("Issuer mismatch: expected %s, got %s", 
                        issuer, unverified_claims.get('iss'))
            raise HTTPException(status_code=401, detail="Invalid token issuer")
            
        # Get signing key
        kid = unverified_headers.get("kid")
        if not kid:
            logger.error("No key ID (kid) in token header")
            raise HTTPException(status_code=401, detail="No key ID in token header")
        
        logger.info("Getting signing key for kid: %s", kid)
        signing_key = await get_signing_key(kid)
        logger.info("Got signing key: %s", signing_key)
        
        if not signing_key:
            logger.error("No signing key found for kid: %s", kid)
            raise HTTPException(status_code=401, detail="No signing key found")
        
        # Construct RSA public key from JWK
        try:
            rsa_key = jwk.construct(signing_key)
            logger.info("Successfully constructed RSA key")
            
            # Verify token
            decoded = jwt.decode(
                token,
                rsa_key.to_pem().decode('utf-8'),
                algorithms=["RS256"],
                options={
                    "verify_aud": False,
                    "verify_exp": True,
                    "verify_iss": True,
                    "verify_sub": True
                }
            )
            logger.info("Token verified successfully")
            logger.info("Decoded token: %s", json.dumps(decoded, indent=2))
            return decoded
            
        except Exception as e:
            logger.error("Failed to verify token: %s", str(e))
            raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")
            
    except Exception as e:
        logger.error("Token verification failed: %s", str(e))
        raise HTTPException(status_code=401, detail=str(e))

async def verify_auth_token_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[dict]:
    """
    Optional token verification that returns None for unauthenticated users
    """
    if not credentials:
        return None
        
    return await get_auth_token(credentials)

# Dependency to use in FastAPI routes
verify_auth_token = get_auth_token

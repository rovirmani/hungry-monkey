from typing import Optional
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import jwt
import httpx
import logging

logger = logging.getLogger(__name__)

class ClerkAuthMiddleware(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(ClerkAuthMiddleware, self).__init__(auto_error=auto_error)
        
        # Get Clerk environment variables
        self.clerk_jwt_key = os.getenv("CLERK_JWT_KEY", "hungry-monkey-jwt")
        self.clerk_issuer = os.getenv("CLERK_JWT_ISSUER")
        if not self.clerk_issuer:
            raise ValueError("CLERK_JWT_ISSUER not found in environment variables")
        
        logger.info("✅ ClerkAuthMiddleware initialized")

    async def verify_jwt(self, token: str) -> bool:
        try:
            # Get the Clerk JWKS
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.clerk_issuer}/.well-known/jwks.json")
                response.raise_for_status()
                jwks = response.json()
            
            # Decode without verification to get the kid
            unverified_header = jwt.get_unverified_header(token)
            
            # Find the signing key
            jwk = None
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    jwk = key
                    break
                    
            if not jwk:
                logger.error("❌ No matching signing key found")
                return False

            # Get the public key
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
            
            # Verify the token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=self.clerk_jwt_key,
                issuer=self.clerk_issuer
            )
            
            logger.info("✅ Token verified successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Token verification failed: {str(e)}")
            return False

    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        try:
            # Skip auth for health check
            if request.url.path == "/api/health":
                logger.info("ℹ️ Skipping auth for health check")
                return None

            # Get credentials
            credentials = await super().__call__(request)
            if not credentials:
                logger.info("👤 No credentials provided")
                return None

            # Verify token
            if not await self.verify_jwt(credentials.credentials):
                logger.error("❌ Invalid token")
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token or expired token",
                )

            logger.info("✅ Request authenticated successfully")
            return credentials

        except Exception as e:
            logger.error(f"❌ Authentication error: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail=str(e)
            )

from typing import Optional
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
from app.auth.clerk import verify_auth_token

logger = logging.getLogger(__name__)

class ClerkAuthMiddleware(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(ClerkAuthMiddleware, self).__init__(auto_error=auto_error)
        logger.info("✅ ClerkAuthMiddleware initialized")

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

            # Verify token using our Clerk SDK auth module
            if not await verify_auth_token(credentials.credentials):
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

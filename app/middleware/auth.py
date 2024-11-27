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
            # Skip auth for health check and other public endpoints
            public_paths = {"/api/health", "/api/docs", "/api/openapi.json", "/openapi.json"}
            if request.url.path in public_paths:
                logger.info(f"ℹ️ Skipping auth for public path: {request.url.path}")
                return None

            # Get credentials
            credentials = await super().__call__(request)
            if not credentials:
                if self.auto_error:
                    raise HTTPException(
                        status_code=401,
                        detail="Authentication required"
                    )
                return None

            # Extract token from Authorization header
            token = credentials.credentials
            if not token:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid authorization header"
                )

            # Verify token using our Clerk SDK auth module
            user_data = await verify_auth_token(token)
            if not user_data:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token or expired token",
                )

            # Add user data to request state for use in route handlers
            request.state.user = user_data
            logger.info(f"✅ Request authenticated successfully for user {user_data['user_id']}")
            return credentials

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Authentication error: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Authentication failed"
            )

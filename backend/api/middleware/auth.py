from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from config.settings import get_settings
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()
settings = get_settings()

async def auth_middleware(request: Request, call_next):
    """
    Middleware for JWT authentication.
    Some endpoints will be public, others will require authentication.
    """
    # List of public endpoints that don't require authentication
    public_paths = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/market",  # Public market data
    ]

    # Check if the path is public
    if any(request.url.path.startswith(path) for path in public_paths):
        return await call_next(request)

    try:
        # Get the JWT token from the request header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=401,
                detail="No authorization header found"
            )

        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication scheme"
            )

        # Verify the JWT token
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            request.state.user = payload
        except JWTError as e:
            logger.error(f"JWT validation error: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return await call_next(request)

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during authentication"
        ) 
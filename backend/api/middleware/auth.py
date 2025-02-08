from fastapi import Request, HTTPException, WebSocket
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from config.settings import get_settings
from typing import Optional, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()
settings = get_settings()

async def create_access_token(data: Dict) -> str:
    """Create a new JWT access token"""
    to_encode = data.copy()
    to_encode.update({
        "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.utcnow()
    })
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)

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
        "/api/market",    # Public market data
        "/api/v1/",      # WebSocket endpoints
        "/api/v1/ws",    # Main WebSocket endpoint
        "/api/v1/market", # Market WebSocket endpoints
        "/api/v1/position" # Position WebSocket endpoints
    ]

    # Check if the path is public
    if any(request.url.path.startswith(path) for path in public_paths):
        return await call_next(request)

    # Skip WebSocket upgrade requests
    if request.headers.get("upgrade", "").lower() == "websocket":
        # For WebSocket requests, we'll handle auth in the WebSocket endpoint
        logger.info("Skipping middleware auth for WebSocket upgrade request")
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
                settings.JWT_SECRET,
                algorithms=[settings.ALGORITHM]
            )
            request.state.user = payload
            logger.info(f"Successfully authenticated user: {payload.get('sub')}")
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

async def validate_token(token: str) -> dict:
    """Validate JWT token and return payload"""
    try:
        logger.info(f"Validating token (first 20 chars): {token[:20]}...")
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM]
        )
        logger.info(f"Token validated successfully for user: {payload.get('sub')}")
        return payload
    except JWTError as e:
        logger.error(f"JWT validation error: {str(e)}")
        logger.error(f"Token that failed validation (first 20 chars): {token[:20]}...")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {str(e)}")
        raise HTTPException(status_code=500, detail="Token validation failed")

async def ws_auth(
    websocket: WebSocket,
    token: Optional[str] = None
) -> dict:
    """Authenticate WebSocket connection"""
    try:
        # Try to get token from query params if not provided
        if not token:
            auth_header = websocket.headers.get("authorization", "")
            logger.info(f"Auth header found: {auth_header[:30]}...")
            token = auth_header.replace("Bearer ", "")
            
        logger.info(f"WS Auth - Attempting authentication with token (first 20 chars): {token[:20] if token else 'None'}...")
        
        if not token:
            logger.error("WS Auth - No token found in headers or query params")
            raise HTTPException(status_code=401, detail="Missing authentication token")
            
        try:
            # Validate the token
            payload = await validate_token(token)
            logger.info(f"WS Auth - Token validated successfully for user: {payload.get('sub')}")
            return payload
        except JWTError as e:
            logger.error(f"WS Auth - Token validation failed: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid token")
            
    except HTTPException as e:
        logger.error(f"WS Auth - Authentication failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"WS Auth - Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication failed") 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api.routes import strategy, position, market
from api.middleware.auth import auth_middleware
from config.settings import get_settings
from config.logging import setup_logging

# Setup logging
setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title="Helenus AI Trading Agent",
    description="Automated trading agent for DeFi protocols",
    version="0.0.1"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware
app.middleware("http")(auth_middleware)

# Include routers
app.include_router(strategy.router, prefix="/api/strategy", tags=["strategy"])
app.include_router(position.router, prefix="/api/position", tags=["position"])
app.include_router(market.router, prefix="/api/market", tags=["market"])

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    ) 
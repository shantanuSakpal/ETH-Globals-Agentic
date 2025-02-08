import os
import sys

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from api.routes import strategy, position, market
from api.middleware.auth import auth_middleware
from core.manager.agent import AgentManager
from config.settings import get_settings
from config.logging import setup_logging
import logging
from api.websocket.routes import router as websocket_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Setup logging
setup_logging()
settings = get_settings()

# Initialize services
agent_manager = AgentManager()

# Initialize FastAPI app
app = FastAPI(
    title="Helenus AI Trading Agent",
    description="Automated trading agent for DeFi protocols",
    version="0.0.1"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Add authentication middleware
app.middleware("http")(auth_middleware)

# Include routers
app.include_router(strategy.router, prefix="/api/strategy", tags=["strategy"])
app.include_router(position.router, prefix="/api/position", tags=["position"])
app.include_router(market.router, prefix="/api/market", tags=["market"])
app.include_router(
    websocket_router,
    prefix="/api/v1",
    tags=["websocket"]
)

@app.on_event("startup")
async def startup_event():
    """Initialize and start agent manager on app startup"""
    await agent_manager.initialize()
    asyncio.create_task(agent_manager.run_agents())

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on app shutdown"""
    #await agent_manager.shutdown()

@app.get("/")
async def root():
    return {
        "name": "Helenus AI Trading Agent",
        "version": "0.0.1",
        "status": "running"
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    ) 
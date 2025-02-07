from fastapi import APIRouter
from .market import router as market_router
from .position import router as position_router
from .strategy import router as strategy_router
from .vault import router as vault_router
from ..websocket.routes import router as websocket_router

api_router = APIRouter()

api_router.include_router(market_router, prefix="/market", tags=["market"])
api_router.include_router(position_router, prefix="/position", tags=["position"])
api_router.include_router(strategy_router, prefix="/strategy", tags=["strategy"])
api_router.include_router(vault_router, prefix="/vault", tags=["vault"])
api_router.include_router(websocket_router, tags=["websocket"])

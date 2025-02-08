from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Any, List
import asyncio
import logging
from datetime import datetime
from backend.api.middleware.auth import ws_auth
from models.websocket import (
    WebSocketMessage,
    WebSocketMessageType,
    PositionUpdate,
    MarketUpdate,
    HealthCheck,
    ErrorMessage,
    StrategyUpdateMessage
)
from services.morpho import MorphoService
from core.dependencies import get_morpho_service

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.start_time = datetime.utcnow()
        
    async def connect(self, websocket: WebSocket, strategy_id: str):
        await websocket.accept()
        if strategy_id not in self.active_connections:
            self.active_connections[strategy_id] = []
        self.active_connections[strategy_id].append(websocket)
        logger.info(f"New WebSocket connection for strategy {strategy_id}")
        
    def disconnect(self, websocket: WebSocket, strategy_id: str):
        if strategy_id in self.active_connections:
            self.active_connections[strategy_id].remove(websocket)
            if not self.active_connections[strategy_id]:
                del self.active_connections[strategy_id]
        logger.info(f"WebSocket disconnected for strategy {strategy_id}")
        
    async def broadcast_to_strategy(self, strategy_id: str, message: Dict[str, Any]):
        if strategy_id in self.active_connections:
            for connection in self.active_connections[strategy_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to strategy {strategy_id}: {str(e)}")
                    
    @property
    def total_connections(self) -> int:
        return sum(len(connections) for connections in self.active_connections.values())
        
    @property
    def uptime(self) -> float:
        return (datetime.utcnow() - self.start_time).total_seconds()

manager = ConnectionManager()

async def position_monitor(
    websocket: WebSocket,
    strategy_id: str,
    morpho_service: MorphoService
):
    """Monitor position and send updates"""
    while True:
        try:
            # Get current position state
            position = await morpho_service.get_position_state(strategy_id)
            
            # Create position update
            update = PositionUpdate(
                strategy_id=strategy_id,
                current_leverage=position.current_leverage,
                current_ltv=position.current_ltv,
                health_factor=position.health_factor,
                total_value_eth=position.total_value_eth,
                total_value_usd=position.total_value_usd,
                estimated_apy=position.estimated_apy
            )
            
            # Create WebSocket message
            message = WebSocketMessage(
                type=WebSocketMessageType.POSITION_UPDATE,
                data=update.dict()
            )
            
            # Send update
            await websocket.send_json(message.dict())
            
            # Wait before next update
            await asyncio.sleep(5)  # Update every 5 seconds
            
        except Exception as e:
            logger.error(f"Error in position monitor: {str(e)}")
            error_message = WebSocketMessage(
                type=WebSocketMessageType.ERROR,
                data=ErrorMessage(
                    code="MONITOR_ERROR",
                    message=str(e)
                ).dict()
            )
            await websocket.send_json(error_message.dict())
            await asyncio.sleep(5)  # Wait before retrying

@router.websocket("/{strategy_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    strategy_id: str,
    morpho_service: MorphoService = Depends(get_morpho_service)
):
    """WebSocket endpoint for strategy-specific connections"""
    try:
        logger.info(f"Incoming WebSocket connection request for strategy {strategy_id}")
        logger.info(f"Headers: {websocket.headers}")
        
        # Accept the WebSocket connection first
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for strategy {strategy_id}")
        
        # Get token from header
        auth_header = websocket.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            logger.error("Missing or invalid authorization header")
            await websocket.close(code=4001)
            return
            
        token = auth_header.replace("Bearer ", "")
        
        try:
            # Validate the token
            await ws_auth(websocket, token)
            logger.info("WebSocket authentication successful")
            
            # Register with connection manager
            await manager.connect(websocket, strategy_id)
            logger.info(f"Connection registered for strategy {strategy_id}")
            
            # Send initial health check
            health_check = WebSocketMessage(
                type=WebSocketMessageType.HEALTH_CHECK,
                data=HealthCheck(
                    uptime=manager.uptime,
                    connected_clients=manager.total_connections,
                    status="connected"
                ).dict()
            )
            await websocket.send_json(health_check.dict())
            
            # Start position monitoring
            monitor_task = asyncio.create_task(
                position_monitor(websocket, strategy_id, morpho_service)
            )
            
            # Message handling loop
            while True:
                try:
                    data = await websocket.receive_text()
                    logger.debug(f"Received message from {strategy_id}: {data[:100]}...")
                    # Process incoming messages
                except WebSocketDisconnect:
                    logger.info(f"WebSocket disconnected for strategy {strategy_id}")
                    break
                    
        except Exception as e:
            logger.error(f"WebSocket processing error: {str(e)}")
            error_msg = WebSocketMessage(
                type=WebSocketMessageType.ERROR,
                data=ErrorMessage(
                    code="PROCESSING_ERROR",
                    message=str(e)
                ).dict()
            )
            await websocket.send_json(error_msg.dict())
            
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
    finally:
        # Cleanup
        if strategy_id in manager.active_connections:
            manager.disconnect(websocket, strategy_id)
        if 'monitor_task' in locals():
            monitor_task.cancel()

@router.get("/health")
async def websocket_health():
    """Get WebSocket server health status"""
    return HealthCheck(
        uptime=manager.uptime,
        connected_clients=manager.total_connections
    ) 
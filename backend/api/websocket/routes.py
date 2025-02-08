from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Optional, Dict
from .protocol import WebSocketProtocol
from .manager import ConnectionManager
from services.monitor import StrategyMonitor
from services.price_feed import PriceFeed
from models.websocket import WSMessage, WSMessageType
from core.agents.morpho.agent import MorphoAgent
from services.websocket import WebSocketService
from services.vault_service import VaultService
from core.manager.agent import AgentManager
from api.middleware.auth import ws_auth
import logging
import json
from datetime import datetime
from api.dependencies import get_connection_manager

router = APIRouter()
logger = logging.getLogger(__name__)
manager = ConnectionManager()

"""
WebSocket Route Handler

This module defines the WebSocket endpoints and handles the initial connection lifecycle.
It serves as the entry point for all WebSocket connections in the application.

Key Components:
- WebSocket endpoint for agent communication
- Authentication middleware integration
- Service initialization
- Message routing
- Error handling

Usage:
    @router.websocket("/ws/agent/{client_id}")
    async def agent_websocket(
        websocket: WebSocket,
        client_id: str,
        user: dict = Depends(ws_auth)
    )
"""

@router.websocket("/ws/agent/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    manager: ConnectionManager = Depends(get_connection_manager)
):
    try:
        # Accept the connection once
        await websocket.accept()
        logger.info(f"Connection accepted for client {client_id}")
        
        # Pass the already-accepted websocket to your connection manager
        await manager.connect(websocket, client_id)
        
        await websocket.send_json({
            "type": "system",
            "data": {"message": "Connected successfully", "client_id": client_id}
        })
        
        while True:
            try:
                data = await websocket.receive_text()
                await websocket.send_text(f"Message received: {data}")
            except WebSocketDisconnect:
                await manager.disconnect(client_id)
                break
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        if client_id in manager.active_connections:
            await manager.disconnect(client_id)

# @router.websocket("/ws/{strategy_id}")
# async def websocket_endpoint(
#     websocket: WebSocket,
#     strategy_id: str,
#     manager: ConnectionManager = Depends(get_connection_manager)
# ):
#     try:
#         # Accept the WebSocket connection first
#         await websocket.accept()
        
#         # Send welcome message
#         await websocket.send_json({
#             "type": "system",
#             "data": {
#                 "message": "Connected to Helenus AI Trading Agent",
#                 "strategy_id": strategy_id,
#                 "timestamp": datetime.now().isoformat()
#             }
#         })
        
#         # Handle messages
#         while True:
#             try:
#                 data = await websocket.receive_text()
#                 # Echo the message back
#                 await websocket.send_json({"type": "echo", "data": data})
#             except WebSocketDisconnect:
#                 break
                
#     except Exception as e:
#         logger.error(f"WebSocket error: {str(e)}")

# @router.websocket("/strategy/{strategy_id}")
# async def strategy_websocket(
#     websocket: WebSocket,
#     strategy_id: str
# ):
#     try:
#         await manager.connect(websocket, strategy_id)
        
#         # Send welcome message
#         await websocket.send_json({
#             "type": "system",
#             "data": {
#                 "message": "Connected to strategy websocket",
#                 "strategy_id": strategy_id
#             }
#         })
        
#         while True:
#             try:
#                 data = await websocket.receive_json()
#                 # Handle received data
#                 await websocket.send_json({
#                     "type": "message",
#                     "data": data
#                 })
#             except WebSocketDisconnect:
#                 await manager.disconnect(strategy_id)
#                 break
                
#     except Exception as e:
#         logger.error(f"WebSocket error: {str(e)}")
#         await manager.disconnect(strategy_id)

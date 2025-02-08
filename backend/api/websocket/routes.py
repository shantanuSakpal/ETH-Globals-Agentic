from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from api.middleware.auth import ws_auth
from services.websocket import WebSocketService
from services.vault_service import VaultService
from core.manager.agent import AgentManager
from services.monitor import StrategyMonitor
from api.dependencies import get_connection_manager
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Instantiate shared service instances.
vault_service = VaultService()
agent_manager = AgentManager()
monitor = StrategyMonitor()
ws_service = WebSocketService(vault_service, agent_manager, monitor)

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
async def agent_websocket(websocket: WebSocket, client_id: str, user: dict = Depends(ws_auth)):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_json()
            message_type = message.get("type")
            data = message.get("data", {})
            response = await ws_service.handle_message(message_type, data, user["id"])
            await websocket.send_json(response)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")

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

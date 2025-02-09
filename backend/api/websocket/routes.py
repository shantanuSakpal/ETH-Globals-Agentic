import logging
import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# Comment out the auth dependency import for hackathon purposes
# from api.middleware.auth import ws_auth
from services.websocket import WebSocketService
from services.vault_service import VaultService
from core.manager.agent import AgentManager
from services.monitor import StrategyMonitor
from api.dependencies import get_connection_manager
from api.websocket.manager import manager
from services.price_feed import PriceFeed

router = APIRouter()
logger = logging.getLogger(__name__)

# Instantiate shared service instances.
vault_service = VaultService()
agent_manager = AgentManager()
price_feed_instance = PriceFeed()
monitor = StrategyMonitor(manager, price_feed_instance)
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
#async def agent_websocket(websocket: WebSocket, client_id: str, user: dict = Depends(ws_auth)):
async def agent_websocket(websocket: WebSocket, client_id: str):
    """
    For hackathon purposes, we're disabling auth. To simulate multiple users,
    we qualify each connection with its unique client_id.
    """
    # Use client_id to generate a unique dummy user for each connection.
    dummy_user = {"id": client_id}
    
    # Step 2: Log unique information to confirm the updated code is running.
    logger.info("Disabled auth route is now active (using dummy users)")
    logger.info(f"Running from: {os.path.abspath(__file__)}")
    logger.info(f"User connected as: {dummy_user['id']}")
    
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_json()
            # Optional: log the received message to observe behavior per user.
            logger.info(f"Received message from {dummy_user['id']}: {message}")
            message_type = message.get("type")
            data = message.get("data", {})
            #response = await ws_service.handle_message(message_type, data, user["id"])
            
            # Use dummy_user["id"] where you'd normally use the authenticated user's ID.
            response = await ws_service.handle_message(message_type, data, dummy_user["id"])
            logger.info(f"Sending response to {dummy_user['id']}: {response}")
            await websocket.send_json(response)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user: {dummy_user['id']}")








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

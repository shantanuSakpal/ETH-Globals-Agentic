from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from typing import Optional
import logging
import uuid
from datetime import datetime
from .manager import manager
from api.middleware.auth import ws_auth
from models.websocket import WSMessage
from fastapi import HTTPException

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    Main WebSocket endpoint for client connections
    """
    client_id = str(uuid.uuid4())
    logger.info(f"New WebSocket connection attempt - Client ID: {client_id}")
    
    try:
        # Token extraction (header override if available)
        auth_header = websocket.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            logger.info(f"Found token in Authorization header for client {client_id}")
        elif token:
            logger.info(f"Using token from query params for client {client_id}")
        else:
            logger.error(f"No token found for client {client_id}")
            await websocket.close(code=4001, reason="Missing authentication token")
            return

        # Accept connection for authentication to occur
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for client {client_id}")

        #         try:
        #     # Authenticate after accepting connection
        #     logger.info(f"Authenticating client {client_id}")
        #     payload = await ws_auth(websocket, token)
        #     logger.info(f"Authentication successful for client {client_id}")
            
        #     # Initialize connection in manager
        #     if await manager.connect(websocket, token, client_id):
        #         logger.info(f"Client {client_id} connected to manager")
                
        #         # Message handling loop
        #         while True:
        #             try:
        #                 message = await websocket.receive_text()
        #                 await manager.handle_message(client_id, message)
        #             except WebSocketDisconnect:
        #                 logger.info(f"Client {client_id} disconnected")
        #                 await manager.disconnect(client_id)
        #                 break
        #     else:
        #         logger.error(f"Manager connection failed for client {client_id}")
        #         await websocket.close(code=4000, reason="Connection failed")
                
        # except HTTPException as e:
        #     logger.error(f"Authentication failed for client {client_id}: {str(e)}")
        #     await websocket.close(code=4001, reason=str(e.detail))
        #     return
        
        # Authenticate the user (using your existing ws_auth or get_user_from_token)
        payload = await ws_auth(websocket, token)
        logger.info(f"Authentication successful for client {client_id}")
        
        # From here, pass the token or user id to your manager or service
        if await manager.connect(websocket, token, client_id):
            logger.info(f"Client {client_id} connected to manager")
            while True:
                try:
                    message = await websocket.receive_text()
                    await manager.handle_message(client_id, message)
                except WebSocketDisconnect:
                    logger.info(f"Client {client_id} disconnected")
                    await manager.disconnect(client_id)
                    break
        else:
            logger.error(f"Manager connection failed for client {client_id}")
            await websocket.close(code=4000, reason="Connection failed")
            
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {str(e)}")
        if not websocket.client_state.DISCONNECTED:
            await websocket.close(code=4000, reason="Internal server error")
        await manager.disconnect(client_id)
        
@router.websocket("/strategy/{strategy_id}")
async def strategy_websocket(
    websocket: WebSocket,
    strategy_id: str,
    token: Optional[str] = Query(None)
):
    """
    Strategy-specific WebSocket endpoint
    """
    client_id = str(uuid.uuid4())
    logger.info(f"New strategy WebSocket connection attempt - Client ID: {client_id}")
    logger.info(f"Headers: {websocket.headers}")
    
    try:
        # Accept the WebSocket connection first
        logger.info("Accepting WebSocket connection...")
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for client {client_id}")
        
        # Get token from header first, then query params
        auth_header = websocket.headers.get("authorization", "")
        logger.info(f"Authorization header: {auth_header}")
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            logger.info(f"Found token in Authorization header for client {client_id}")
        elif token:
            logger.info(f"Using token from query params for client {client_id}")
        else:
            logger.error(f"No token found for client {client_id}")
            await websocket.close(code=4001, reason="Missing authentication token")
            return

        try:
            # Authenticate after accepting connection
            logger.info(f"Authenticating client {client_id}")
            payload = await ws_auth(websocket, token)
            logger.info(f"Authentication successful for client {client_id}")
            
            # Initialize connection in manager
            if await manager.connect(websocket, token, client_id):
                logger.info(f"Client {client_id} connected to manager")
                
                # Subscribe to strategy updates
                await manager._handle_subscribe(
                    client_id,
                    {
                        "type": "subscribe",
                        "data": {"topics": [f"strategy_{strategy_id}"]}
                    }
                )
                
                # Message handling loop
                while True:
                    try:
                        message = await websocket.receive_text()
                        await manager.handle_message(client_id, message)
                    except WebSocketDisconnect:
                        logger.info(f"Client {client_id} disconnected")
                        await manager.disconnect(client_id)
                        break
            else:
                logger.error(f"Manager connection failed for client {client_id}")
                await websocket.close(code=4000, reason="Connection failed")
                
        except HTTPException as e:
            logger.error(f"Authentication failed for client {client_id}: {str(e)}")
            await websocket.close(code=4001, reason=str(e.detail))
            return
            
    except Exception as e:
        logger.error(f"Strategy WebSocket error for client {client_id}: {str(e)}")
        if not websocket.client_state.DISCONNECTED:
            await websocket.close(code=4000, reason="Internal server error")
        await manager.disconnect(client_id)
        
@router.websocket("/market/{symbol}")
async def market_websocket(
    websocket: WebSocket,
    symbol: str,
    token: Optional[str] = Query(None)
):
    """
    Market data WebSocket endpoint
    
    Args:
        websocket: WebSocket connection
        symbol: Market symbol
        token: Authentication token
    """
    client_id = str(uuid.uuid4())
    
    try:
        # Authenticate connection
        await ws_auth(websocket, token)
        
        # Accept connection
        if not await manager.connect(websocket, token, client_id):
            await websocket.close(code=4000, reason="Connection failed")
            return
            
        # Subscribe to market updates
        await manager._handle_subscribe(
            client_id,
            {
                "type": "subscribe",
                "data": {"topics": [f"market_{symbol}"]}
            }
        )
        
        # Message handling loop
        while True:
            try:
                message = await websocket.receive_text()
                await manager.handle_message(client_id, message)
            except WebSocketDisconnect:
                await manager.disconnect(client_id)
                break
                
    except Exception as e:
        logger.error(f"Market WebSocket error for client {client_id}: {str(e)}")
        await manager.disconnect(client_id)
        
@router.websocket("/position/{position_id}")
async def position_websocket(
    websocket: WebSocket,
    position_id: str,
    token: Optional[str] = Query(None)
):
    """
    Position-specific WebSocket endpoint
    
    Args:
        websocket: WebSocket connection
        position_id: Position identifier
        token: Authentication token
    """
    client_id = str(uuid.uuid4())
    
    try:
        # Authenticate connection
        await ws_auth(websocket, token)
        
        # Accept connection
        if not await manager.connect(websocket, token, client_id):
            await websocket.close(code=4000, reason="Connection failed")
            return
            
        # Subscribe to position updates
        await manager._handle_subscribe(
            client_id,
            {
                "type": "subscribe",
                "data": {"topics": [f"position_{position_id}"]}
            }
        )
        
        # Message handling loop
        while True:
            try:
                message = await websocket.receive_text()
                await manager.handle_message(client_id, message)
            except WebSocketDisconnect:
                await manager.disconnect(client_id)
                break
                
    except Exception as e:
        logger.error(f"Position WebSocket error for client {client_id}: {str(e)}")
        await manager.disconnect(client_id) 
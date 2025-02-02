from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Any
import logging
import json
import uuid
from datetime import datetime
from .connection import ConnectionManager
from models.websocket import WSMessageType

logger = logging.getLogger(__name__)
manager = ConnectionManager()

async def handle_websocket_connection(websocket: WebSocket):
    """
    Handle new WebSocket connections and message routing
    
    Args:
        websocket: The WebSocket connection
    """
    client_id = str(uuid.uuid4())
    
    try:
        await manager.connect(websocket, client_id)
        
        # Start sending market updates to the client
        await send_welcome_message(client_id)
        
        while True:
            try:
                message = await websocket.receive_text()
                await manager.handle_client_message(client_id, message)
            except WebSocketDisconnect:
                manager.disconnect(client_id)
                break
            except Exception as e:
                logger.error(f"Error handling message: {str(e)}")
                await send_error_message(client_id, str(e))
                
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(client_id)

async def send_welcome_message(client_id: str):
    """
    Send welcome message to new client
    
    Args:
        client_id: ID of the client
    """
    await manager.send_personal_message(
        client_id,
        {
            "type": WSMessageType.MARKET_UPDATE,
            "data": {
                "message": "Welcome to Helenus AI Trading Agent",
                "supported_topics": [
                    "market_updates",
                    "strategy_updates",
                    "position_updates"
                ]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )

async def send_error_message(client_id: str, error_message: str):
    """
    Send error message to client
    
    Args:
        client_id: ID of the client
        error_message: Error message to send
    """
    await manager.send_personal_message(
        client_id,
        {
            "type": WSMessageType.ERROR,
            "data": {"message": error_message},
            "timestamp": datetime.utcnow().isoformat()
        }
    )

async def broadcast_market_update(market_data: Dict[str, Any]):
    """
    Broadcast market update to subscribed clients
    
    Args:
        market_data: Market data to broadcast
    """
    await manager.broadcast(
        {
            "type": WSMessageType.MARKET_UPDATE,
            "data": market_data,
            "timestamp": datetime.utcnow().isoformat()
        },
        "market_updates"
    )

async def broadcast_strategy_update(strategy_data: Dict[str, Any]):
    """
    Broadcast strategy update to subscribed clients
    
    Args:
        strategy_data: Strategy data to broadcast
    """
    await manager.broadcast(
        {
            "type": WSMessageType.STRATEGY_UPDATE,
            "data": strategy_data,
            "timestamp": datetime.utcnow().isoformat()
        },
        "strategy_updates"
    )

async def broadcast_position_update(position_data: Dict[str, Any]):
    """
    Broadcast position update to subscribed clients
    
    Args:
        position_data: Position data to broadcast
    """
    await manager.broadcast(
        {
            "type": WSMessageType.POSITION_UPDATE,
            "data": position_data,
            "timestamp": datetime.utcnow().isoformat()
        },
        "position_updates"
    )

# Helper function to format timestamps
def get_timestamp() -> str:
    """Get current UTC timestamp in ISO format"""
    return datetime.utcnow().isoformat()

# Error handling decorator
def websocket_error_handler(func):
    """Decorator for handling WebSocket errors"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except WebSocketDisconnect:
            # Handle normal disconnection
            client_id = kwargs.get("client_id")
            if client_id:
                manager.disconnect(client_id)
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"WebSocket error in {func.__name__}: {str(e)}")
            client_id = kwargs.get("client_id")
            if client_id:
                await send_error_message(client_id, str(e))
    return wrapper 
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Optional
from .manager import ConnectionManager
from agents.morpho_agent import MorphoAgent
from models.websocket import WSMessage
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
manager = ConnectionManager()

@router.websocket("/ws/agent/{client_id}")
async def agent_websocket(
    websocket: WebSocket,
    client_id: str,
    agent: MorphoAgent = Depends(get_agent)
):
    """WebSocket endpoint for agent communication"""
    try:
        await manager.connect(websocket, client_id)
        
        # Send initial state
        await websocket.send_json({
            "type": "connection_established",
            "data": {
                "client_id": client_id,
                "agent_status": await agent.get_status()
            }
        })
        
        while True:
            try:
                # Receive and process messages
                data = await websocket.receive_json()
                message = WSMessage(**data)
                
                # Process message based on type
                response = await process_ws_message(message, agent)
                
                # Send response back to client
                await websocket.send_json(response)
                
            except ValueError as e:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": f"Invalid message format: {str(e)}"}
                })
                
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await manager.disconnect(websocket)

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Optional
from .manager import ConnectionManager
from backend.core.agents.morpho.agent import MorphoAgent
from models.websocket import WSMessage
import logging
from services.websocket import WebSocketService
from services.vault_service import VaultService
from core.manager.agent import AgentManager

router = APIRouter()
logger = logging.getLogger(__name__)
manager = ConnectionManager()

@router.websocket("/ws/agent/{client_id}")
async def agent_websocket(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for agent communication"""
    try:
        await manager.connect(websocket, client_id)
        ws_service = WebSocketService(vault_service=VaultService(), agent_manager=AgentManager())
        
        while True:
            try:
                data = await websocket.receive_json()
                response = await ws_service.handle_message(
                    message_type=data.get("type"),
                    data=data.get("data", {}),
                    user_id=client_id
                )
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

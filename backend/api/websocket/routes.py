from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Optional
from .protocol import WebSocketProtocol
from .manager import ConnectionManager
from services.monitor import StrategyMonitor
from services.price_feed import PriceFeed
from models.websocket import WSMessage, WSMessageType
from backend.core.agents.morpho.agent import MorphoAgent
from services.websocket import WebSocketService
from services.vault_service import VaultService
from core.manager.agent import AgentManager
from api.middleware.auth import ws_auth
import logging
import json
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)
manager = ConnectionManager()
monitor = StrategyMonitor(manager, PriceFeed())

@router.websocket("/ws/agent/{client_id}")
async def agent_websocket(
    websocket: WebSocket,
    client_id: str,
    user: dict = Depends(ws_auth)
):
    protocol = None
    try:
        # Initialize services with manager
        ws_service = WebSocketService(
            vault_service=VaultService(manager=manager),
            agent_manager=AgentManager()
        )
        
        # Initialize protocol handler
        protocol = WebSocketProtocol(websocket)
        await protocol.accept()
        
        # Add user info from JWT
        protocol.user_id = user["sub"]
        
        # Connect to manager
        await manager.connect(protocol, client_id)
        
        # Start message queue processing
        await manager._message_queue.start_processing()
        
        # Send welcome message
        await protocol.send({
            "type": WSMessageType.SYSTEM,
            "data": {
                "message": "Connected to Helenus AI Trading Agent",
                "client_id": client_id,
                "timestamp": datetime.now().isoformat()
            }
        })
        
        # Message handling loop
        async for message in protocol.iter_messages():
            if message.type == "pong":
                continue
                
            if message.type == WSMessageType.STRATEGY_SELECT:
                # Start monitoring and subscribe to updates
                await monitor.start_monitoring(message.data["vault_id"])
                await manager.subscribe(client_id, f"strategy_{message.data['vault_id']}")
            
            # Handle message through WebSocket service
            response = await ws_service.handle_message(
                message_type=message.type,
                data=message.data,
                user_id=client_id
            )
            await protocol.send(response)
            
            # Queue message for additional processing if needed
            await manager._message_queue.put_message(message)
            
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected")
    finally:
        if protocol:
            await manager.disconnect(client_id)

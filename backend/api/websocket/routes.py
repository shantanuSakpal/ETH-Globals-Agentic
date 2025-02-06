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
async def agent_websocket(
    websocket: WebSocket,
    client_id: str,
    user: dict = Depends(ws_auth)
):
    protocol = None
    try:
        # Initialize services
        monitor = StrategyMonitor(manager, PriceFeed())
        ws_service = WebSocketService(
            vault_service=VaultService(manager=manager),
            agent_manager=AgentManager(),
            monitor=monitor
        )
        
        # Initialize protocol handler
        protocol = WebSocketProtocol(websocket)
        await protocol.accept()
        
        # Add user info from JWT
        protocol.user_id = user["sub"]
        
        # Connect and start queue
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
            try:
                #if message.type == WSMessageType.STRATEGY_SELECT:
                #     response = await ws_service.process_strategy_selection(
                #         message.data,
                #         user["sub"]
                #     )
                    
                #     if response["type"] == WSMessageType.STRATEGY_INIT:
                #         # subscribe to the vault
                        
                #         #await monitor.start_monitoring(response["data"]["vault_id"])
                #         await manager.subscribe(
                #             client_id, 
                #             f"strategy_{response['data']['vault_id']}"
                #         )
                        
                #         # Queue background processing
                #         await manager._message_queue.put_message(WSMessage(
                #             type=WSMessageType.AGENT_START,
                #             data={
                #                 "vault_id": response["data"]["vault_id"],
                #                   "client_id": client_id
                #             }
                #         ))
                    
                #     await protocol.send(response)
                    
                # elif message.type == "pong":
                #     continue
                    
                # else:
                #     response = await ws_service.handle_message(
                #         message_type=message.type,
                #         data=message.data,
                #         user_id=client_id
                #     )
                #     await protocol.send(response)
                    
                #     # Queue for background processing if needed
                #     await manager._message_queue.put_message(message)
                # Route all messages through WebSocketService
                response = await ws_service.handle_message(
                    message_type=message.type,
                    data=message.data,
                    user_id=user["sub"]
                )
                
                # Handle special cases after business logic
                if response["type"] == WSMessageType.STRATEGY_INIT:
                    await manager.subscribe(
                        client_id, 
                        f"strategy_{response['data']['vault_id']}"
                    )
                    
                    await manager._message_queue.put_message(WSMessage(
                        type=WSMessageType.AGENT_START,
                        data={
                            "vault_id": response["data"]["vault_id"],
                            "client_id": client_id
                        }
                    ))
                
                await protocol.send(response)
                
            except Exception as e:
                await protocol.send({
                    "type": WSMessageType.ERROR,
                    "data": {"message": str(e)}
                })
                
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected")
    finally:
        if protocol:
            await manager.disconnect(client_id)

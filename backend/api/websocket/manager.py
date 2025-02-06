from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Any, Optional
from datetime import datetime
import asyncio
import logging
from models.websocket import WSMessageType, WSMessage
from .protocol import WebSocketProtocol
from .queue import MessageQueue

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self._protocols: Dict[str, WebSocketProtocol] = {}
        self._subscriptions: Dict[str, Set[str]] = {}
        self._message_queue = MessageQueue()
        
        # Register message handlers
        self._message_queue._handlers = {
            WSMessageType.STRATEGY_SELECT: self._handle_strategy_select,
            WSMessageType.MONITOR_UPDATE: self._handle_monitor_update,
            WSMessageType.AGENT_START: self._handle_agent_start
            #WSMessageType.DEPOSIT: self._handle_deposit
        }

    async def connect(self, protocol: WebSocketProtocol, client_id: str) -> None:
        """Register new WebSocket connection"""
        self._protocols[client_id] = protocol
        self._subscriptions[client_id] = set()

    async def disconnect(self, client_id: str) -> None:
        """Handle client disconnection"""
        if protocol := self._protocols.pop(client_id, None):
            await protocol.close()
        self._subscriptions.pop(client_id, None)

    async def broadcast(self, message: dict, topic: Optional[str] = None) -> None:
        disconnected = []
        for client_id, protocol in self._protocols.items():
            try:
                await protocol.send(message)
            except Exception:
                disconnected.append(client_id)
                
        for client_id in disconnected:
            await self.disconnect(client_id)

    async def _heartbeat(self, client_id: str) -> None:
        """Send periodic heartbeat to check connection"""
        while True:
            try:
                if client_id not in self._protocols:
                    break
                    
                protocol = self._protocols[client_id]
                await protocol.send({
                    "type": "ping",
                    "timestamp": datetime.now().isoformat()
                })
                await asyncio.sleep(30)  # 30 second heartbeat
                
            except WebSocketDisconnect:
                await self.disconnect(client_id)
                break
            except Exception as e:
                logger.error(f"Heartbeat error for {client_id}: {str(e)}")
                await self.disconnect(client_id)
                break

    async def broadcast_message(self, message: WSMessage, topic: Optional[str] = None) -> None:
        """Broadcast message to subscribers"""
        disconnected = []
        
        for client_id, protocol in self._protocols.items():
            # Skip if client not subscribed to topic
            if topic and topic not in self._subscriptions[client_id]:
                continue
                
            try:
                await protocol.send(message.dict())
            except Exception as e:
                logger.error(f"Failed to send to {client_id}: {str(e)}")
                disconnected.append(client_id)
                
        # Clean up disconnected clients
        for client_id in disconnected:
            await self.disconnect(client_id)

    async def subscribe(self, client_id: str, topic: str) -> None:
        """Subscribe client to a topic"""
        if client_id not in self._subscriptions:
            self._subscriptions[client_id] = set()
        self._subscriptions[client_id].add(topic)
        
        # Send confirmation
        if protocol := self._protocols.get(client_id):
            await protocol.send({
                "type": "subscription_confirmed",
                "data": {"topic": topic},
                "timestamp": datetime.utcnow().isoformat()
            })
            
    async def unsubscribe(self, client_id: str, topic: str) -> None:
        """Unsubscribe client from a topic"""
        if client_id in self._subscriptions:
            self._subscriptions[client_id].discard(topic)

    async def _handle_agent_start(self, message: WSMessage):
        """Handle agent initialization in background"""
        try:
            vault_id = message["data"]["vault_id"]
            client_id = message["data"]["client_id"]
            
            # Background processing for agent setup
            await self._protocols[client_id].send({
                "type": WSMessageType.AGENT_STARTED,
                "data": {
                    "vault_id": vault_id,
                    "status": "running"
                }
            })
        except Exception as e:
            logger.error(f"Error in agent start handler: {str(e)}")

    async def _handle_strategy_select(self, message: WSMessage):
        """Handle strategy selection messages"""
        if client_id := message.data.get("client_id"):
            await self.broadcast_message(
                message=message,
                topic=f"strategy_{message.data['vault_id']}"
            )

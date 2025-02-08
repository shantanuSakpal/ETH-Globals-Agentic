from typing import Dict, Set, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
import logging
import json
import asyncio
from datetime import datetime
from models.websocket import WSMessage, WSMessageType
from api.websocket.queue import MessageQueue
from api.middleware.auth import validate_token
from core.manager.agent import AgentManager

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections and message broadcasting"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = {}
        self.message_queue = MessageQueue()
        self.agent_manager = AgentManager()
        self._cleanup_task = None
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize the WebSocket manager"""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        await self.agent_manager.initialize()
        
    async def connect(self, websocket: WebSocket, client_id: str) -> bool:
        """Connect a new client"""
        try:
            self.active_connections[client_id] = websocket
            await self.broadcast_status(client_id, "connected")
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {str(e)}")
            return False
            
    async def disconnect(self, client_id: str):
        """Disconnect a client"""
        if client_id in self.active_connections:
            await self.broadcast_status(client_id, "disconnected")
            del self.active_connections[client_id]
            
        if client_id in self.subscriptions:
            del self.subscriptions[client_id]
            
        self.logger.info(f"Client {client_id} disconnected")
        
    async def broadcast_status(self, client_id: str, status: str):
        message = {
            "type": "status",
            "data": {
                "client_id": client_id,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
        }
        await self.broadcast(message)

    async def broadcast(self, message: dict):
        disconnected = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(client_id)
        
        for client_id in disconnected:
            await self.disconnect(client_id)

    async def send_personal_message(self, client_id: str, message: WSMessage):
        """Send message to specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message.dict())
            except Exception as e:
                logger.error(f"Failed to send personal message: {str(e)}")
                await self.disconnect(client_id)

    async def handle_message(self, client_id: str, message_text: str):
        """Handle incoming WebSocket messages"""
        try:
            message = json.loads(message_text)
            message_type = message.get("type")
            
            handlers = {
                WSMessageType.SUBSCRIBE: self._handle_subscribe,
                WSMessageType.UNSUBSCRIBE: self._handle_unsubscribe,
                "strategy_select": self._handle_strategy_select,
                "position_update": self._handle_position_update,
                "strategy_update": self._handle_strategy_update
            }
            
            handler = handlers.get(message_type)
            if handler:
                await handler(client_id, message)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from client {client_id}")
            await self.send_error(client_id, "Invalid message format")
        except Exception as e:
            logger.error(f"Message handling error: {str(e)}")
            await self.send_error(client_id, str(e))

    async def send_error(self, client_id: str, error_message: str):
        """Send error message to client"""
        await self.send_personal_message(
            client_id,
            WSMessage(
                type=WSMessageType.ERROR,
                data={"message": error_message},
                timestamp=datetime.utcnow().isoformat()
            )
        )
        
    async def _handle_subscribe(self, client_id: str, data: dict):
        """Handle subscription requests"""
        topics = data.get("data", {}).get("topics", [])
        if client_id in self.subscriptions:
            self.subscriptions[client_id].update(topics)
            
        await self.send_personal_message(
            client_id,
            WSMessage(
                type=WSMessageType.SUBSCRIBE,
                data={"topics": list(self.subscriptions[client_id])},
                timestamp=datetime.utcnow().isoformat()
            )
        )
        
    async def _handle_unsubscribe(self, client_id: str, data: dict):
        """Handle unsubscribe requests"""
        topics = data.get("data", {}).get("topics", [])
        if client_id in self.subscriptions:
            self.subscriptions[client_id].difference_update(topics)
            
        await self.send_personal_message(
            client_id,
            WSMessage(
                type=WSMessageType.UNSUBSCRIBE,
                data={"topics": list(self.subscriptions[client_id])},
                timestamp=datetime.utcnow().isoformat()
            )
        )
        
    async def _handle_strategy_select(self, client_id: str, data: dict):
        """Handle strategy selection"""
        try:
            strategy_data = data.get("data", {})
            
            # Initialize strategy
            strategy_id = await self.agent_manager.create_strategy(
                strategy_data
            )
            
            # Send confirmation
            await self.send_personal_message(
                client_id,
                WSMessage(
                    type="strategy_init",
                    data={
                        "strategy_id": strategy_id,
                        "status": "initialized",
                        "config": strategy_data
                    },
                    timestamp=datetime.utcnow().isoformat()
                )
            )
            
            # Subscribe to strategy updates
            self.subscriptions[client_id].add(f"strategy_{strategy_id}")
            
        except Exception as e:
            logger.error(f"Strategy initialization failed: {str(e)}")
            await self.send_error(client_id, str(e))
            
    async def _handle_position_update(self, client_id: str, data: dict):
        """Handle position update requests"""
        try:
            position_data = data.get("data", {})
            position_id = position_data.get("position_id")
            
            # Update position
            updated = await self.agent_manager.update_position(
                position_id,
                position_data
            )
            
            # Broadcast update
            await self.broadcast_message(
                WSMessage(
                    type=WSMessageType.POSITION_UPDATE,
                    data=updated,
                    timestamp=datetime.utcnow().isoformat()
                ),
                f"position_{position_id}"
            )
            
        except Exception as e:
            logger.error(f"Position update failed: {str(e)}")
            await self.send_error(client_id, str(e))
            
    async def _handle_strategy_update(self, client_id: str, data: dict):
        """Handle strategy update requests"""
        try:
            strategy_data = data.get("data", {})
            strategy_id = strategy_data.get("strategy_id")
            
            # Update strategy
            updated = await self.agent_manager.update_strategy(
                strategy_id,
                strategy_data
            )
            
            # Broadcast update
            await self.broadcast_message(
                WSMessage(
                    type=WSMessageType.STRATEGY_UPDATE,
                    data=updated,
                    timestamp=datetime.utcnow().isoformat()
                ),
                f"strategy_{strategy_id}"
            )
            
        except Exception as e:
            logger.error(f"Strategy update failed: {str(e)}")
            await self.send_error(client_id, str(e))
            
    async def _cleanup_loop(self):
        """Periodic cleanup of inactive connections"""
        while True:
            try:
                # Ping all connections
                disconnected = []
                for client_id, websocket in self.active_connections.items():
                    try:
                        await websocket.send_json({
                            "type": "ping",
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    except Exception:
                        disconnected.append(client_id)
                        
                # Cleanup disconnected
                for client_id in disconnected:
                    await self.disconnect(client_id)
                    
            except Exception as e:
                logger.error(f"Cleanup error: {str(e)}")
                
            await asyncio.sleep(30)  # Run every 30 seconds

    async def cleanup(self):
        """Cleanup resources"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            
        # Close all connections
        for client_id in list(self.active_connections.keys()):
            await self.disconnect(client_id)
            
        # Cleanup agent manager
        await self.agent_manager.cleanup()

# Global WebSocket manager instance
manager = ConnectionManager()

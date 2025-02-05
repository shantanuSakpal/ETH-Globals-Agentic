from fastapi import WebSocket
from typing import Dict, Set, Any
import logging
from datetime import datetime
from models.websocket import WSMessage, WSMessageType

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = set()
        self.connection_metadata[client_id] = {
            "connected_at": datetime.now().isoformat(),
            "message_count": 0
        }
        logger.info(f"Client {client_id} connected")

    async def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            del self.subscriptions[client_id]
            del self.connection_metadata[client_id]
            logger.info(f"Client {client_id} disconnected")

    async def broadcast(self, message_type: WSMessageType, data: Dict[str, Any]):
        disconnected = []
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json({
                    "type": message_type,
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                })
                self.connection_metadata[client_id]["message_count"] += 1
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {str(e)}")
                disconnected.append(client_id)

        for client_id in disconnected:
            await self.disconnect(client_id)

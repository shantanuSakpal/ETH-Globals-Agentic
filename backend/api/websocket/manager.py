from fastapi import WebSocket
from typing import Set, Dict, Any
import logging
import json
from enum import Enum

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, client_id: str = None):
        """Connect new client and store metadata"""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.connection_metadata[websocket] = {
            "client_id": client_id,
            "connected_at": datetime.now().isoformat(),
            "message_count": 0
        }
        logger.info(f"New client connected. Total connections: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        """Disconnect client and cleanup"""
        self.active_connections.remove(websocket)
        self.connection_metadata.pop(websocket, None)
        logger.info(f"Client disconnected. Remaining connections: {len(self.active_connections)}")

    async def broadcast(self, message_type: str, data: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        disconnected = set()
        message = self._format_message(message_type, data)
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
                self.connection_metadata[connection]["message_count"] += 1
            except Exception as e:
                logger.error(f"Error broadcasting to client: {str(e)}")
                disconnected.add(connection)
                
        # Cleanup disconnected clients
        for connection in disconnected:
            await self.disconnect(connection)

    def _format_message(self, message_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format message with standard structure"""
        return {
            "type": message_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

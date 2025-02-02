from fastapi import WebSocket
from typing import Dict, Set, Any
import logging
import json
import asyncio
from models.websocket import WSMessage, WSMessageType

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    Manages WebSocket connections and message broadcasting
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = {}  # client_id -> set of subscriptions
        
    async def connect(self, websocket: WebSocket, client_id: str):
        """
        Accept a new WebSocket connection
        
        Args:
            websocket: The WebSocket connection
            client_id: Unique identifier for the client
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = set()
        logger.info(f"Client {client_id} connected")
        
    def disconnect(self, client_id: str):
        """
        Handle client disconnection
        
        Args:
            client_id: ID of the client to disconnect
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.subscriptions:
            del self.subscriptions[client_id]
        logger.info(f"Client {client_id} disconnected")
        
    async def subscribe(self, client_id: str, topics: list):
        """
        Subscribe a client to specific topics
        
        Args:
            client_id: ID of the client
            topics: List of topics to subscribe to
        """
        if client_id in self.subscriptions:
            self.subscriptions[client_id].update(topics)
            await self.send_personal_message(
                client_id,
                {
                    "type": WSMessageType.SUBSCRIBE,
                    "data": {"topics": topics},
                    "timestamp": ""  # Add timestamp here
                }
            )
            logger.info(f"Client {client_id} subscribed to topics: {topics}")
            
    async def unsubscribe(self, client_id: str, topics: list):
        """
        Unsubscribe a client from specific topics
        
        Args:
            client_id: ID of the client
            topics: List of topics to unsubscribe from
        """
        if client_id in self.subscriptions:
            self.subscriptions[client_id].difference_update(topics)
            await self.send_personal_message(
                client_id,
                {
                    "type": WSMessageType.UNSUBSCRIBE,
                    "data": {"topics": topics},
                    "timestamp": ""  # Add timestamp here
                }
            )
            logger.info(f"Client {client_id} unsubscribed from topics: {topics}")
            
    async def broadcast(self, message: Dict[str, Any], topic: str):
        """
        Broadcast a message to all subscribed clients
        
        Args:
            message: Message to broadcast
            topic: Topic of the message
        """
        disconnected_clients = []
        
        for client_id, subscriptions in self.subscriptions.items():
            if topic in subscriptions:
                try:
                    websocket = self.active_connections[client_id]
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to client {client_id}: {str(e)}")
                    disconnected_clients.append(client_id)
                    
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
            
    async def send_personal_message(self, client_id: str, message: Dict[str, Any]):
        """
        Send a message to a specific client
        
        Args:
            client_id: ID of the client
            message: Message to send
        """
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to client {client_id}: {str(e)}")
                self.disconnect(client_id)
                
    async def handle_client_message(self, client_id: str, message: str):
        """
        Handle incoming messages from clients
        
        Args:
            client_id: ID of the client
            message: Raw message from the client
        """
        try:
            data = json.loads(message)
            msg_type = data.get("type")
            
            if msg_type == WSMessageType.SUBSCRIBE:
                topics = data.get("data", {}).get("topics", [])
                await self.subscribe(client_id, topics)
                
            elif msg_type == WSMessageType.UNSUBSCRIBE:
                topics = data.get("data", {}).get("topics", [])
                await self.unsubscribe(client_id, topics)
                
            else:
                logger.warning(f"Unknown message type from client {client_id}: {msg_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message from client {client_id}")
            await self.send_personal_message(
                client_id,
                {
                    "type": WSMessageType.ERROR,
                    "data": {"message": "Invalid message format"},
                    "timestamp": ""  # Add timestamp here
                }
            )
        except Exception as e:
            logger.error(f"Error handling message from client {client_id}: {str(e)}")
            
    async def start_heartbeat(self):
        """
        Start sending heartbeat messages to all connected clients
        """
        while True:
            disconnected_clients = []
            
            for client_id, websocket in self.active_connections.items():
                try:
                    await websocket.send_json({
                        "type": "heartbeat",
                        "timestamp": ""  # Add timestamp here
                    })
                except Exception as e:
                    logger.error(f"Heartbeat failed for client {client_id}: {str(e)}")
                    disconnected_clients.append(client_id)
                    
            # Clean up disconnected clients
            for client_id in disconnected_clients:
                self.disconnect(client_id)
                
            await asyncio.sleep(30)  # Send heartbeat every 30 seconds 
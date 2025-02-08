import asyncio
import websockets
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketTestClient:
    """Test client for WebSocket connections"""
    
    def __init__(
        self,
        url: str = "ws://localhost:8000/api/v1",
        token: Optional[str] = None
    ):
        self.url = url
        self.token = token
        self.websocket = None
        self.strategy_id = None
        self.received_messages = []
        
    async def connect_to_strategy(self, client_id: str):
        """Connect to strategy-specific WebSocket endpoint"""
        try:
            logger.info(f"Connecting to URL: {self.url}")
            self.websocket = await websockets.connect(
                self.url
            )
            self.strategy_id = client_id
            logger.info("Connected successfully")
            # Start message handler task if needed.
            asyncio.create_task(self._handle_messages())
            return True
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            return False
            
    async def disconnect(self):
        """Close WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from WebSocket")
            
    async def _handle_messages(self):
        """Handle incoming messages"""
        try:
            while True:
                if self.websocket:
                    message = await self.websocket.recv()
                    data = json.loads(message)
                    self.received_messages.append(data)
                    self._log_message(data)
                else:
                    break
        except Exception as e:
            logger.error(f"Message handling error: {str(e)}")
            
    def _log_message(self, message: Dict[str, Any]):
        """Log received message based on type"""
        msg_type = message.get("type")
        
        if msg_type == "position_update":
            data = message["data"]
            logger.info(
                f"Position Update - "
                f"Leverage: {data['current_leverage']}, "
                f"LTV: {data['current_ltv']}, "
                f"Health: {data['health_factor']}, "
                f"Value: ${data['total_value_usd']}"
            )
        elif msg_type == "health_check":
            data = message["data"]
            logger.info(
                f"Health Check - "
                f"Status: {data['status']}, "
                f"Uptime: {data['uptime']}s, "
                f"Clients: {data['connected_clients']}"
            )
        elif msg_type == "error":
            data = message["data"]
            logger.error(f"Error Message - {data['message']}")
        else:
            logger.info(f"Message Received - Type: {msg_type}")
            
    def get_latest_position(self) -> Optional[Dict[str, Any]]:
        """Get latest position update"""
        position_updates = [
            msg["data"] for msg in self.received_messages
            if msg["type"] == "position_update"
        ]
        return position_updates[-1] if position_updates else None
        
    def get_connection_health(self) -> Optional[Dict[str, Any]]:
        """Get latest health check"""
        health_checks = [
            msg["data"] for msg in self.received_messages
            if msg["type"] == "health_check"
        ]
        return health_checks[-1] if health_checks else None

    async def send_message(self, message: Dict[str, Any]):
        """Send message to WebSocket server"""
        if self.websocket:
            await self.websocket.send(json.dumps(message))
        else:
            logger.error("WebSocket not connected")

async def run_test():
    """Run WebSocket integration test"""
    # Create test client
    client = WebSocketTestClient()
    
    try:
        # Connect to test strategy
        strategy_id = "test-strategy-1"
        success = await client.connect_to_strategy(strategy_id)
        
        if not success:
            logger.error("Failed to connect to WebSocket")
            return
            
        # Wait for initial messages
        await asyncio.sleep(2)
        
        # Check health status
        health = client.get_connection_health()
        if health:
            logger.info(
                f"Connection healthy - "
                f"Uptime: {health['uptime']}s, "
                f"Clients: {health['connected_clients']}"
            )
        
        # Wait for position updates
        logger.info("Waiting for position updates...")
        await asyncio.sleep(10)
        
        # Check latest position
        position = client.get_latest_position()
        if position:
            logger.info(
                f"Latest Position - "
                f"Leverage: {position['current_leverage']}, "
                f"Health Factor: {position['health_factor']}"
            )
            
        # Test complete
        logger.info(
            f"Test complete - "
            f"Received {len(client.received_messages)} messages"
        )
        
    except Exception as e:
        logger.error(f"Test error: {str(e)}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(run_test()) 
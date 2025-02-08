import pytest
import asyncio
import logging
from websocket_test import WebSocketTestClient
from api.middleware.auth import create_access_token

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_test_token():
    test_user = {"sub": "test-user", "role": "agent"}
    token = await create_access_token(test_user)
    logger.info(f"Generated test token: {token[:20]}...")  # Log part of the token for debugging
    return token

@pytest.mark.asyncio
async def test_agent_connection():
    client_id = "test-client-123"
    
    # Use the correct endpoint.
    client = WebSocketTestClient(
        url=f"ws://localhost:8000/api/v1/ws/agent/{client_id}"
    )
    
    try:
        connected = await client.connect_to_strategy(client_id)
        assert connected is True
        
        # Optionally verify connection properties.
        assert client.websocket is not None
        assert client.websocket.open is True
        
    finally:
        if client.websocket:
            await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_agent_connection()) 
import pytest
import asyncio
from tests.websocket_test import WebSocketTestClient
from main import app

# Dummy token for authentication
DUMMY_TOKEN = "dummy_token"
# Ensure the URL matches your running WebSocket endpoint
WS_URL = "ws://localhost:8000/api/v1/ws/agent/test_client"

# # Override ws_auth dependency to always return a dummy user.
# def override_ws_auth(websocket: WebSocket):
#     return {"id": "dummy_user_id"}

# # Import the actual ws_auth from your middleware
# from api.middleware.auth import ws_auth

# # Correctly override the dependency
# app.dependency_overrides[ws_auth] = override_ws_auth

@pytest.mark.asyncio
async def test_full_backend_lifecycle_with_custom_client():
    """
    Integration test using the custom WebSocketTestClient to simulate:
    1. WebSocket connection and authentication.
    2. Strategy selection -- triggering vault and agent creation.
    3. Deposit process -- triggering vault deposit actions.
    4. Validating responses for strategy initialization and deposit completion.
    """
    # Instantiate the custom WebSocket client with the URL and token.
    client = WebSocketTestClient(url=WS_URL, token=DUMMY_TOKEN)
    
    # Connect to the WebSocket endpoint.
    connected = await client.connect_to_strategy("test_client")
    assert connected, "Failed to connect to WebSocket"

    # --- Step 1: Send strategy_select message ---
    strategy_select_payload = {
        "type": "strategy_select",
        "data": {
            "strategy_id": "eth-usdc-loop",
            "initial_deposit": 100,
            "parameters": {
                "collateralAmount": 100,
                "maxLeverage": 3.0,
                "minCollateralRatio": 1.5,
                "targetApy": 10.0,
                "rebalanceThreshold": 5.0,
                "slippageTolerance": 0.5,
                "riskLevel": "Low"
            }
            # Omitting "agent_wallet_data" to force auto wallet creation.
        }
    }
    await client.send_message(strategy_select_payload)
    
    # Give the server some time to process and respond with a strategy_init message.
    await asyncio.sleep(5)
    
    # Check for the 'strategy_init' message in the received messages.
    strategy_init_message = next(
        (msg for msg in client.received_messages if msg.get("type") == "strategy_init"), 
        None
    )
    assert strategy_init_message is not None, "Did not receive strategy_init message"
    
    init_data = strategy_init_message.get("data", {})
    vault_id = init_data.get("vault_id")
    assert vault_id is not None, "Vault ID is missing in the strategy_init message"
    
    init_text = init_data.get("message", "").lower()
    assert "fund" in init_text, "Initialization instructions should include wallet funding information"
    
    # --- Step 2: Send deposit message ---
    deposit_payload = {
        "type": "deposit",
        "data": {
            "vault_id": vault_id
            # Additional deposit fields may be added if needed.
        }
    }
    await client.send_message(deposit_payload)
    
    # Wait for the deposit processing response.
    await asyncio.sleep(1)
    
    deposit_response = next(
        (msg for msg in client.received_messages if msg.get("type") == "deposit_complete"), 
        None
    )
    assert deposit_response is not None, "Did not receive deposit_complete message"
    
    # Optional: Verify for additional monitor_update messages received.
    monitor_update = next(
        (msg for msg in client.received_messages if msg.get("type") == "monitor_update"), 
        None
    )
    # Uncomment the following line if you require monitor updates in your test.
    # assert monitor_update is not None, "Did not receive any monitor_update messages"
    
    # Disconnect the client to clean up.
    await client.disconnect() 
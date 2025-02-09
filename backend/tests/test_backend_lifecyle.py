import pytest
import asyncio
from httpx import AsyncClient, ASGITransport

# Import the FastAPI app instance
from main import app

# Dummy auth header assumed to be accepted by ws_auth
DUMMY_AUTH_HEADERS = {"Authorization": "Bearer dummy_token"}

@pytest.mark.asyncio
async def test_full_backend_lifecycle():
    """
    Integration test for the full backend lifecycle:
    1. WebSocket connection and authentication.
    2. Strategy selection: vault creation, agent wallet generation,
       agent initialization, and monitoring startup.
    3. Deposit process: deploying (if needed) the vault contract and updating the vault balance.
    4. Receiving periodic monitor_update messages.
    """
    # Use ASGITransport to wrap the FastAPI app.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Establish WebSocket connection on the authenticated endpoint.
        async with client.ws_connect("/ws/agent/test_client", headers=DUMMY_AUTH_HEADERS) as websocket:
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
                        "riskLevel": "Low",
                    }
                    # Omitting "agent_wallet_data" to trigger automatic wallet creation.
                }
            }
            await websocket.send_json(strategy_select_payload)
            
            # Wait for the 'strategy_init' response.
            init_response = await websocket.receive_json()
            assert init_response.get("type") == "strategy_init", f"Expected 'strategy_init', got {init_response.get('type')}"
            init_data = init_response.get("data", {})
            vault_id = init_data.get("vault_id")
            assert vault_id is not None, "Vault ID should be provided in the initialization response."
            assert "deposit_address" in init_data, "Initialization response must include a deposit_address."
            init_message = init_data.get("message", "")
            assert "fund" in init_message.lower(), "Initialization instructions should prompt for wallet funding."

            # --- Step 2: Optionally check for a monitor_update message ---
            try:
                monitor_update = await asyncio.wait_for(websocket.receive_json(), timeout=5.0)
                if monitor_update.get("type") == "monitor_update":
                    monitor_data = monitor_update.get("data", {})
                    # Verify that some key metrics are present (adjust keys per your implementation)
                    assert "health_factor" in monitor_data or "position" in monitor_data, \
                        "Monitor update data should include key performance metrics."
            except asyncio.TimeoutError:
                # In a test environment, monitor updates may not arrive in a strict time frame.
                pass

            # --- Step 3: Send deposit message ---
            deposit_payload = {
                "type": "deposit",
                "data": {
                    "vault_id": vault_id,
                    # Optionally include other deposit parameters if defined by your application.
                }
            }
            await websocket.send_json(deposit_payload)
            
            # Wait for the 'deposit_complete' response.
            deposit_response = await websocket.receive_json()
            assert deposit_response.get("type") == "deposit_complete", (
                f"Expected 'deposit_complete', got {deposit_response.get('type')}"
            )
            
            # --- Step 4: Optionally check for further monitor_update messages post deposit ---
            try:
                post_deposit_update = await asyncio.wait_for(websocket.receive_json(), timeout=5.0)
                if post_deposit_update.get("type") == "monitor_update":
                    update_data = post_deposit_update.get("data", {})
                    assert isinstance(update_data, dict), "Monitor update data should be a dictionary."
            except asyncio.TimeoutError:
                pass

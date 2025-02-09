async def test_full_backend_lifecycle_with_custom_client():
    client = WebSocketTestClient(url=WS_URL, token=DUMMY_TOKEN)
    try:
        # ... test logic ...
    finally:
        await client.disconnect()
        # Add agent cleanup
        await agent_manager.cleanup_test_agents()
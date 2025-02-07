from fastapi import WebSocket
from .websocket.manager import ConnectionManager
from .middleware.auth import ws_auth  # Another dependency example

_manager = None

async def get_connection_manager():
    global _manager
    if _manager is None:
        _manager = ConnectionManager()
    return _manager

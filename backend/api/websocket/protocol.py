from fastapi import WebSocket, WebSocketDisconnect
from typing import AsyncIterator, Optional
import asyncio
import logging
from models.websocket import WSMessage

logger = logging.getLogger(__name__)

class WebSocketProtocol:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.connected = False
        self._ping_task: Optional[asyncio.Task] = None
        
    async def accept(self) -> None:
        await self.websocket.accept()
        self.connected = True
        self._ping_task = asyncio.create_task(self._ping_loop())
        
    async def _ping_loop(self) -> None:
        while self.connected:
            try:
                await self.websocket.send_bytes(b'ping')
                await asyncio.sleep(20)
            except Exception:
                break
                
    async def iter_messages(self) -> AsyncIterator[WSMessage]:
        while self.connected:
            try:
                data = await self.websocket.receive_text()
                message = WSMessage.model_validate_json(data)
                yield message
            except WebSocketDisconnect:
                self.connected = False
                break
                
    async def send(self, message: dict) -> None:
        if self.connected:
            await self.websocket.send_json(message)
            
    async def close(self, code: int = 1000) -> None:
        self.connected = False
        if self._ping_task:
            self._ping_task.cancel()
        await self.websocket.close(code=code)

    # async def handle_strategy_message(self, message: WSMessage) -> None:
    #     """Handle strategy selection and initialization"""
    #     try:
    #         # Create vault
    #         response = await self.ws_service.process_strategy_selection(
    #             message.data, 
    #             self.client_id
    #         )
            
    #         # Initialize strategy
    #         if response["type"] == "strategy_initialized":
    #             await self.agent_manager.initialize_strategy(
    #                 response["data"]["vault_id"]
    #             )
                
    #         await self.send(response)
    #     except Exception as e:
    #         logger.error(f"Strategy handling error: {e}")
    #         await self.send({
    #             "type": "error",
    #             "data": {"message": str(e)}
    #         })

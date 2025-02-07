from typing import Dict, Any, Callable, Awaitable, Optional
import asyncio
import logging
from models.websocket import WSMessage, WSMessageType
from datetime import datetime

logger = logging.getLogger(__name__)

class MessageQueue:
    def __init__(self, max_size: int = 1000):
        #self.queue = asyncio.Queue(maxsize=max_size)
        self.queue = asyncio.PriorityQueue(maxsize=max_size)
        self._handlers: Dict[WSMessageType, Callable] = {}
        self._background_task: Optional[asyncio.Task] = None
        
    async def start_processing(self):
        if self._background_task is None:
            self._background_task = asyncio.create_task(self._process_queue())
            
    async def stop(self):
        if self._background_task:
            self._background_task.cancel()
            try:
                await self._background_task
            except asyncio.CancelledError:
                pass
            self._background_task = None
            
    async def _process_queue(self):
        while True:
            try:
                priority, message = await self.queue.get()
                if handler := self._handlers.get(message.type):
                    await handler(message)
                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
            
    async def put_message(self, message: WSMessage, priority: int = 2):
        """Add message to queue with priority (1=high, 2=normal, 3=low)"""
        try:
            await asyncio.wait_for(
                #self.queue.put(message),
                self.queue.put((priority, message)),
                timeout=1.0
            )
        except asyncio.TimeoutError:
            logger.warning("Queue full - message dropped")
    
    #  def register_handler(self, message_type: str, handler: Callable[[WSMessage], Awaitable[None]]):
    def register_handler(self, message_type: WSMessageType, handler: Callable[[WSMessage], Awaitable[None]]):
        """Register a handler for a specific message type"""
        self._handlers[message_type] = handler
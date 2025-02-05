from typing import Dict, Any, Callable, Awaitable
import asyncio
import logging
from models.websocket import WSMessage
from datetime import datetime

logger = logging.getLogger(__name__)

class MessageQueue:
    def __init__(self, max_size: int = 1000):
        self.queue = asyncio.Queue(maxsize=max_size)
        self._background_task: asyncio.Task | None = None
        self._handlers: Dict[str, Callable[[WSMessage], Awaitable[None]]] = {}
        
    async def start_processing(self):
        """Start the message processing loop"""
        self._background_task = asyncio.create_task(self._process_queue())
        
    async def _process_queue(self):
        """Process messages from the queue"""
        while True:
            message = await self.queue.get()
            try:
                # Get handler for message type
                if handler := self._handlers.get(message.type):
                    await handler(message)
                else:
                    logger.warning(f"No handler for message type: {message.type}")
                    
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
            finally:
                self.queue.task_done()
                
    async def put_message(self, message: WSMessage):
        """Add message to queue with backpressure"""
        try:
            await self.queue.put(message)
        except asyncio.QueueFull:
            logger.warning("Message queue full, applying backpressure")
            await asyncio.sleep(1)  # Wait before retrying
            await self.put_message(message)
            
    def register_handler(self, message_type: str, handler: Callable[[WSMessage], Awaitable[None]]):
        """Register a handler for a specific message type"""
        self._handlers[message_type] = handler
        
    async def stop(self):
        """Stop queue processing"""
        if self._background_task:
            self._background_task.cancel()
            try:
                await self._background_task
            except asyncio.CancelledError:
                pass
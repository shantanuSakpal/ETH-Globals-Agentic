from typing import Dict, Any, Callable, Awaitable, Optional
import asyncio
import logging
from models.websocket import WSMessage, WSMessageType
from datetime import datetime

logger = logging.getLogger(__name__)

class MessageQueue:
    def __init__(self, max_size: int = 1000):

        # self._background_task: asyncio.Task | None = None
        # self._handlers: Dict[str, Callable[[WSMessage], Awaitable[None]]] = {}

        self.queue = asyncio.Queue(maxsize=max_size)
        self._handlers: Dict[WSMessageType, Callable] = {}
        self._background_task: Optional[asyncio.Task] = None
        self._priority_queue = asyncio.PriorityQueue(maxsize=max_size)
        
    async def start_processing(self):
        """Start the message processing loop"""
        self._background_task = asyncio.create_task(self._process_queue())
        
    async def _process_queue(self):
        """Process messages from the queue"""
        while True:
              #message = await self.queue.get()
            try:
                #   # Get handler for message type
                # if handler := self._handlers.get(message.type):
                #     await handler(message)
                # else:
                #     logger.warning(f"No handler for message type: {message.type}")
                priority, message = await self._priority_queue.get()
                handler = self._handlers.get(message.type)
                
                if handler:
                    try:
                        await handler(message)
                    except Exception as e:
                        logger.error(f"Handler error: {str(e)}")
                        
                self._priority_queue.task_done()
                
            except Exception as e:
            #         logger.error(f"Error processing message: {str(e)}")
            # finally:
            #     self.queue.task_done()
                logger.error(f"Queue processing error: {str(e)}")
                await asyncio.sleep(1)
                
    #  async def put_message(self, message: WSMessage):
    #     """Add message to queue with backpressure"""
    async def put_message(self, message: WSMessage, priority: int = 2):
        """Add message to queue with priority (1=high, 2=normal, 3=low)"""
        try:
        #         await self.queue.put(message)
        # except asyncio.QueueFull:
        #     logger.warning("Message queue full, applying backpressure")
        #     await asyncio.sleep(1)  # Wait before retrying
        #     await self.put_message(message)
        
            await asyncio.wait_for(
                self._priority_queue.put((priority, message)),
                timeout=1.0
            )
        except asyncio.TimeoutError:
            logger.warning("Queue full - message dropped")
            
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
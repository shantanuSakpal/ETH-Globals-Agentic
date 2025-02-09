from typing import Dict, Any, Callable, Awaitable, Optional
import asyncio
import logging
from datetime import datetime
from models.websocket import WSMessage

logger = logging.getLogger(__name__)

class MessageQueue:
    """
    Asynchronous message queue for handling WebSocket messages.
    Provides message buffering and ordered processing.
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize message queue
        
        Args:
            max_size: Maximum queue size
        """
        self.queue = asyncio.Queue(maxsize=max_size)
        self.handlers: Dict[str, Callable[[WSMessage], Awaitable[None]]] = {}
        self._processor_task: Optional[asyncio.Task] = None
        self._running = False
        
    async def start(self):
        """Start message processing"""
        if not self._running:
            self._running = True
            self._processor_task = asyncio.create_task(self._process_messages())
            logger.info("Message queue processor started")
            
    async def stop(self):
        """Stop message processing"""
        self._running = False
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
            self._processor_task = None
            logger.info("Message queue processor stopped")
            
    def register_handler(
        self,
        message_type: str,
        handler: Callable[[WSMessage], Awaitable[None]]
    ):
        """
        Register a message handler
        
        Args:
            message_type: Type of message to handle
            handler: Async handler function
        """
        self.handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type}")
        
    async def put_message(self, message: WSMessage):
        """
        Add message to queue
        
        Args:
            message: Message to queue
        """
        try:
            await self.queue.put(message)
        except asyncio.QueueFull:
            logger.error("Message queue full, dropping message")
            
    async def _process_messages(self):
        """Process messages from queue"""
        while self._running:
            try:
                message = await self.queue.get()
                
                try:
                    await self._handle_message(message)
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                finally:
                    self.queue.task_done()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in message processor: {str(e)}")
                await asyncio.sleep(1)  # Prevent tight loop on error
                
    async def _handle_message(self, message: WSMessage):
        """
        Handle a single message
        
        Args:
            message: Message to handle
        """
        handler = self.handlers.get(message.type)
        if handler:
            try:
                await handler(message)
            except Exception as e:
                logger.error(f"Error in message handler: {str(e)}")
        else:
            logger.warning(f"No handler for message type: {message.type}")
            
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        return {
            "queue_size": self.queue.qsize(),
            "handlers": list(self.handlers.keys()),
            "running": self._running,
            "timestamp": datetime.utcnow().isoformat()
        }
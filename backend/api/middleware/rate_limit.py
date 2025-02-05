from datetime import datetime, timedelta
from typing import Dict, DefaultDict
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class WebSocketRateLimiter:
    def __init__(self, rate_limit: int = 60):  # messages per minute
        self.rate_limit = rate_limit
        self.message_counts: DefaultDict[str, list] = defaultdict(list)
        
    async def is_allowed(self, client_id: str) -> bool:
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old messages
        self.message_counts[client_id] = [
            ts for ts in self.message_counts[client_id] 
            if ts > minute_ago
        ]
        
        if len(self.message_counts[client_id]) >= self.rate_limit:
            logger.warning(f"Rate limit exceeded for client {client_id}")
            return False
            
        self.message_counts[client_id].append(now)
        return True

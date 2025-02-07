from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Callable
from enum import Enum
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)

class WSMessageType(str, Enum):
    STRATEGY_SELECT = "strategy_select"
    STRATEGY_INIT = "strategy_init"
    AGENT_START = "agent_start"
    MONITOR_UPDATE = "monitor_update"
    SYSTEM = "system"
    ERROR = "error"
    PONG = "pong"

class WSMessage(BaseModel):
    """WebSocket message model"""
    type: WSMessageType
    data: Dict[str, Any]
    request_id: Optional[str] = Field(None, description="Client-provided request ID for correlation")

class WSStrategyMessage(BaseModel):
    strategy_type: str
    parameters: Dict[str, Any]
    user_id: str

class WSResponse(BaseModel):
    type: WSMessageType
    data: Dict[str, Any]
    request_id: Optional[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class WSTopicPrefix(str, Enum):
    STRATEGY = "strategy"
    VAULT = "vault"
    MARKET = "market"
    SYSTEM = "system"

    def format(self, identifier: str) -> str:
        return f"{self.value}_{identifier}"

class WSTopicFormatter:
    @staticmethod
    def format_topic(prefix: WSTopicPrefix, identifier: str) -> str:
        return f"{prefix}_{identifier}"

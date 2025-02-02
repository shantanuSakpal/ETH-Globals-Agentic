from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from enum import Enum

class WSMessageType(str, Enum):
    STRATEGY_COMMAND = "strategy_command"
    MARKET_QUERY = "market_query"
    POSITION_QUERY = "position_query"
    MARKET_UPDATE = "market_update"
    POSITION_UPDATE = "position_update"
    ERROR = "error"

class WSMessage(BaseModel):
    """WebSocket message model"""
    type: WSMessageType
    data: Dict[str, Any]
    request_id: Optional[str] = Field(None, description="Client-provided request ID for correlation")

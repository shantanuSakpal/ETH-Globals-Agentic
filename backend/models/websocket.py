from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime

class WSMessageType(str, Enum):
    STRATEGY_SELECT = "strategy_select"
    # MARKET_QUERY = "market_query"
    # POSITION_QUERY = "position_query"
    # MARKET_UPDATE = "market_update"
    # POSITION_UPDATE = "position_update"
    STRATEGY_INIT = "strategy_init"
    AGENT_START = "agent_start"
    MONITOR_UPDATE = "monitor_update"
    SYSTEM = "system"
    ERROR = "error"
    PONG = "pong"
    BALANCE_UPDATE = "balance_update"
    STRATEGY_SELECTED = "strategy_selected"
    STRATEGY_INITIALIZED = "strategy_initialized"
    AGENT_STARTED = "agent_started"
    MONITORING_STARTED = "monitoring_started"
    DEPOSIT_REQUIRED = "deposit_required"

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

class WSTopicFormatter:
    @staticmethod
    def format_topic(prefix: WSTopicPrefix, identifier: str) -> str:
        return f"{prefix}_{identifier}"

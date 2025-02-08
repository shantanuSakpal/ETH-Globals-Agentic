from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Callable, List
from enum import Enum
from datetime import datetime
import asyncio
import logging
from decimal import Decimal

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

class WebSocketMessageType(str, Enum):
    POSITION_UPDATE = "position_update"
    MARKET_UPDATE = "market_update"
    HEALTH_CHECK = "health_check"
    ERROR = "error"
    STRATEGY_UPDATE = "strategy_update"

class WebSocketMessage(BaseModel):
    """Base WebSocket message model"""
    type: WebSocketMessageType
    timestamp: datetime = datetime.utcnow()
    data: Dict[str, Any]

class PositionUpdate(BaseModel):
    """Real-time position update data"""
    strategy_id: str
    current_leverage: Decimal
    current_ltv: Decimal
    health_factor: Decimal
    total_value_eth: Decimal
    total_value_usd: Decimal
    estimated_apy: Decimal
    price_impact: Optional[Decimal] = None
    warning_level: Optional[str] = None

class MarketUpdate(BaseModel):
    """Real-time market update data"""
    market_id: str
    supply_apy: Decimal
    borrow_apy: Decimal
    utilization_rate: Decimal
    oracle_price: Decimal
    available_liquidity: Decimal

class HealthCheck(BaseModel):
    """Health check response"""
    status: str = "ok"
    uptime: float
    connected_clients: int

class ErrorMessage(BaseModel):
    """Error message"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class StrategyUpdateMessage(BaseModel):
    """Strategy update notification"""
    strategy_id: str
    update_type: str
    old_values: Optional[Dict[str, Any]] = None
    new_values: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()

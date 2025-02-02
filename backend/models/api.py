from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class StrategyStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"

class StrategyBase(BaseModel):
    name: str = Field(..., description="Name of the strategy")
    description: str = Field(..., description="Description of the strategy")
    risk_level: RiskLevel = Field(..., description="Risk level of the strategy")
    target_apy: float = Field(..., ge=0, description="Target APY in percentage")
    max_leverage: float = Field(..., ge=1, description="Maximum leverage ratio")
    rebalance_threshold: float = Field(..., ge=0, description="Rebalance threshold in percentage")

class StrategyCreate(StrategyBase):
    initial_capital: float = Field(..., gt=0, description="Initial capital in USD")
    asset_pair: str = Field(..., description="Trading pair (e.g., 'ETH-USDC')")

class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    risk_level: Optional[RiskLevel] = None
    target_apy: Optional[float] = Field(None, ge=0)
    max_leverage: Optional[float] = Field(None, ge=1)
    rebalance_threshold: Optional[float] = Field(None, ge=0)
    status: Optional[StrategyStatus] = None

class StrategyResponse(StrategyBase):
    id: str = Field(..., description="Unique identifier of the strategy")
    status: StrategyStatus = Field(..., description="Current status of the strategy")
    current_apy: Optional[float] = Field(None, description="Current APY being achieved")
    current_leverage: Optional[float] = Field(None, description="Current leverage ratio")
    total_value: Optional[float] = Field(None, description="Total value in USD")

class StrategyList(BaseModel):
    strategies: List[StrategyResponse]

# Position Models
class PositionType(str, Enum):
    LONG = "long"
    SHORT = "short"

class PositionStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    LIQUIDATED = "liquidated"

class PositionCreate(BaseModel):
    strategy_id: str
    position_type: PositionType
    size: float = Field(..., gt=0)
    leverage: float = Field(..., ge=1)
    stop_loss: Optional[float] = Field(None, ge=0)
    take_profit: Optional[float] = Field(None, ge=0)

class PositionUpdate(BaseModel):
    size: Optional[float] = Field(None, gt=0)
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class PositionResponse(BaseModel):
    id: str
    strategy_id: str
    position_type: PositionType
    status: PositionStatus
    size: float
    leverage: float
    entry_price: float
    current_price: float
    pnl: float
    pnl_percentage: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    created_at: str
    updated_at: str

# Market Data Models
class MarketData(BaseModel):
    symbol: str
    price: float
    timestamp: str
    volume_24h: float
    change_24h: float
    high_24h: float
    low_24h: float

class MarketDataList(BaseModel):
    markets: List[MarketData]

# WebSocket Models
class WSMessageType(str, Enum):
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    MARKET_UPDATE = "market_update"
    POSITION_UPDATE = "position_update"
    STRATEGY_UPDATE = "strategy_update"
    ERROR = "error"

class WSMessage(BaseModel):
    type: WSMessageType
    data: dict
    timestamp: str 
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from decimal import Decimal
from enum import Enum
from datetime import datetime

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class StrategyStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"

class LeverageMode(str, Enum):
    CONSERVATIVE = "conservative"  # Lower leverage, higher safety
    MODERATE = "moderate"         # Balanced approach
    AGGRESSIVE = "aggressive"     # Higher leverage, higher risk

class StrategyBase(BaseModel):
    """Base strategy configuration"""
    name: str = Field(..., description="Strategy name")
    description: str = Field(..., description="Strategy description")
    risk_level: RiskLevel = Field(..., description="Risk level")
    leverage_mode: LeverageMode = Field(..., description="Leverage mode")
    target_ltv: Decimal = Field(
        ...,
        gt=0,
        lt=1,
        description="Target Loan-to-Value ratio"
    )
    max_ltv: Decimal = Field(
        ...,
        gt=0,
        lt=1,
        description="Maximum allowed LTV before rebalancing"
    )
    min_collateral_ratio: Decimal = Field(
        ...,
        gt=1,
        description="Minimum collateral ratio to maintain"
    )
    rebalance_threshold: Decimal = Field(
        ...,
        gt=0,
        lt=1,
        description="LTV threshold that triggers rebalancing"
    )
    emergency_exit_threshold: Decimal = Field(
        ...,
        gt=0,
        lt=1,
        description="LTV threshold that triggers emergency exit"
    )
    max_slippage: Decimal = Field(
        default=Decimal("0.005"),
        ge=0,
        le=Decimal("0.1"),
        description="Maximum allowed slippage for trades"
    )
    loop_interval: int = Field(
        default=3600,
        ge=300,
        description="Time between leverage loops in seconds"
    )

class MorphoMarketInfo(BaseModel):
    """Current market information from Morpho"""
    supply_apy: Decimal
    borrow_apy: Decimal
    available_liquidity: Decimal
    total_supplied: Decimal
    total_borrowed: Decimal
    utilization_rate: Decimal
    oracle_price: Decimal
    updated_at: datetime

class StrategyCreate(BaseModel):
    """Input model for creating a new strategy"""
    initial_deposit_eth: Decimal = Field(..., description="Initial ETH deposit amount")
    target_leverage: Decimal = Field(..., description="Target leverage ratio")
    leverage_mode: LeverageMode = Field(default=LeverageMode.MODERATE)
    max_slippage: Decimal = Field(default=Decimal("0.005"))
    stop_loss: Optional[Decimal] = Field(default=None, description="Stop loss threshold in %")
    take_profit: Optional[Decimal] = Field(default=None, description="Take profit threshold in %")

class StrategyUpdate(BaseModel):
    """Input model for updating strategy parameters"""
    target_leverage: Optional[Decimal] = None
    leverage_mode: Optional[LeverageMode] = None
    max_slippage: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None

class StrategyState(BaseModel):
    """Current state of a strategy position"""
    current_leverage: Decimal
    current_ltv: Decimal
    eth_collateral: Decimal
    usdc_borrowed: Decimal
    total_value_eth: Decimal
    total_value_usd: Decimal
    health_factor: Decimal
    estimated_apy: Decimal
    next_rebalance: datetime
    last_updated: datetime

class StrategyResponse(BaseModel):
    """Response model for strategy operations"""
    strategy_id: str
    owner_address: str
    created_at: datetime
    updated_at: datetime
    parameters: StrategyCreate
    current_state: StrategyState
    market_info: MorphoMarketInfo

class StrategyList(BaseModel):
    """List of strategies"""
    strategies: List[StrategyResponse]

    @validator("strategies")
    def sort_by_created(cls, v):
        return sorted(v, key=lambda x: x.created_at, reverse=True)

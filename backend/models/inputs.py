from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class StrategyType(str, Enum):
    YIELD_FARMING = "yield_farming"
    LEVERAGE = "leverage"
    LENDING = "lending"
    LIQUIDITY_PROVISIONING = "liquidity_provisioning"

class StrategySelectionInput(BaseModel):
    strategy_type: StrategyType
    initial_deposit: float = Field(..., gt=0)
    token_address: str
    risk_level: Optional[str] = "moderate"

class DepositInput(BaseModel):
    vault_id: str
    amount: float = Field(..., gt=0)
    token_address: str
    slippage: Optional[float] = Field(default=0.01, ge=0, le=1)

class UserDepositInput(BaseModel):
    vault_id: str
    token_address: str
    amount: float = Field(..., gt=0)
    slippage: Optional[float] = Field(default=0.01, ge=0, le=1)

class VaultActionInput(BaseModel):
    vault_id: str
    action_type: str
    params: dict

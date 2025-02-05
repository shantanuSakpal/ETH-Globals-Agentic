from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from models.api import RiskLevel, StrategyStatus, PositionType, PositionStatus
import uuid

class StrategyDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    risk_level: RiskLevel
    status: StrategyStatus = StrategyStatus.ACTIVE
    parameters: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class VaultDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    strategy_id: str
    status: str = "pending"
    initial_deposit: float
    current_balance: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PositionDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    vault_id: str
    position_type: PositionType
    size: float
    leverage: float
    entry_price: float
    current_price: float
    pnl: float
    status: PositionStatus
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

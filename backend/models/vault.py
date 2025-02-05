from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime

class VaultStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"

class VaultCreate(BaseModel):
    strategy_id: str
    initial_deposit: float
    user_id: str
    settings: Optional[Dict[str, Any]] = None

class Vault(BaseModel):
    id: str
    user_id: str
    strategy_id: str
    status: VaultStatus
    balance: float
    created_at: datetime
    updated_at: datetime
    settings: Optional[Dict[str, Any]] = None

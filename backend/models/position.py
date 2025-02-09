from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from enum import Enum

class PositionType(str, Enum):
    LONG = "long"
    SHORT = "short"

class PositionStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    LIQUIDATED = "liquidated"

class PositionCreate(BaseModel):
    """Parameters for creating a new position"""
    strategy_id: str = Field(..., description="ID of the strategy to use")
    size: Decimal = Field(..., gt=0, description="Size of the position in base currency")
    leverage: Decimal = Field(..., ge=1, description="Leverage ratio for the position")
    position_type: PositionType = Field(..., description="Type of position (long/short)")
    
class PositionUpdate(BaseModel):
    """Parameters for updating an existing position"""
    size: Optional[Decimal] = Field(None, gt=0, description="New size for the position")
    leverage: Optional[Decimal] = Field(None, ge=1, description="New leverage ratio")
    stop_loss: Optional[Decimal] = Field(None, ge=0, description="Stop loss price level")
    take_profit: Optional[Decimal] = Field(None, ge=0, description="Take profit price level")

class PositionResponse(BaseModel):
    """Response model for position operations"""
    id: str = Field(..., description="Unique position identifier")
    strategy_id: str = Field(..., description="ID of the associated strategy")
    size: Decimal = Field(..., description="Current position size")
    leverage: Decimal = Field(..., description="Current leverage ratio")
    position_type: PositionType = Field(..., description="Type of position")
    entry_price: Decimal = Field(..., description="Entry price of the position")
    current_price: Decimal = Field(..., description="Current market price")
    pnl: Decimal = Field(..., description="Current profit/loss")
    status: PositionStatus = Field(..., description="Current position status")
    stop_loss: Optional[Decimal] = Field(None, description="Stop loss price level")
    take_profit: Optional[Decimal] = Field(None, description="Take profit price level")
    created_at: datetime = Field(..., description="Position creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class PositionList(BaseModel):
    """Response model for listing positions"""
    positions: List[PositionResponse] = Field(..., description="List of positions") 
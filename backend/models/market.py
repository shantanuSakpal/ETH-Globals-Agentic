from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal

class MarketData(BaseModel):
    """Model for market data"""
    symbol: str
    price: Decimal
    timestamp: int
    volume_24h: Optional[Decimal] = None
    change_24h: Optional[Decimal] = None
    market_cap: Optional[Decimal] = None
    
    class Config:
        json_encoders = {
            Decimal: str
        }

class MarketDataList(BaseModel):
    """Model for a list of market data"""
    data: List[MarketData]
    
    class Config:
        json_encoders = {
            Decimal: str
        } 
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class WalletCreate(BaseModel):
    user_id: str
    
class WalletDB(BaseModel):
    id: str
    user_id: str
    cdp_wallet_id: str
    address: str
    created_at: datetime
    updated_at: datetime
    status: str = "active"
    
class Wallet(BaseModel):
    id: str
    user_id: str
    address: str
    status: str
    created_at: datetime
    updated_at: datetime

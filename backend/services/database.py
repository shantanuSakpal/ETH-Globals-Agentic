from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from models.database import StrategyDB, VaultDB, PositionDB
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, mongodb_url: str):
        self.client = AsyncIOMotorClient(mongodb_url)
        self.db = self.client.helenus
        
    async def create_strategy(self, strategy: StrategyDB) -> str:
        result = await self.db.strategies.insert_one(strategy.dict())
        return str(result.inserted_id)
        
    async def create_vault(self, vault: VaultDB) -> str:
        result = await self.db.vaults.insert_one(vault.dict())
        return str(result.inserted_id)
        
    async def get_vault(self, vault_id: str) -> Optional[VaultDB]:
        result = await self.db.vaults.find_one({"id": vault_id})
        return VaultDB(**result) if result else None

    async def update_vault_balance(self, vault_id: str, new_balance: float):
        await self.db.vaults.update_one(
            {"id": vault_id},
            {"$set": {
                "current_balance": new_balance,
                "updated_at": datetime.utcnow()
            }}
        )

    async def update_vault_settings(self, vault_id: str, new_settings: dict):
        await self.db.vaults.update_one(
            {"id": vault_id},
            {"$set": {
                "settings": new_settings,
                "updated_at": datetime.utcnow()
            }}
        )

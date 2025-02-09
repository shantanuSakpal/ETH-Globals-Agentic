from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from models.database import StrategyDB, VaultDB, PositionDB, WalletDB
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, mongodb_url: str):
        self.client = AsyncIOMotorClient(mongodb_url)
        self.db = self.client.helenus2
        
    async def create_strategy(self, strategy: StrategyDB) -> str:
        result = await self.db.strategies.insert_one(strategy.model_dump())
        return str(result.inserted_id)
        
    async def create_vault(self, vault: VaultDB) -> str:
        result = await self.db.vaults.insert_one(vault.model_dump())
        return str(result.inserted_id)
        
    async def get_vault(self, vault_id: str) -> Optional[VaultDB]:
        result = await self.db.vaults.find_one({"id": vault_id})
        return VaultDB(**result) if result else None

    async def update_vault_balance(self, vault_id: str, new_balance: float):
        await self.db.vaults.update_one(
            {"id": vault_id},
            {"$set": {
                "current_balance": new_balance,
                "updated_at": datetime.now()
            }}
        )

    async def update_vault_settings(self, vault_id: str, new_settings: dict):
        await self.db.vaults.update_one(
            {"id": vault_id},
            {"$set": {
                "settings": new_settings,
                "updated_at": datetime.now()
            }}
        )

    async def get_agent_wallet(self, wallet_id: str) -> Optional[WalletDB]:
        """
        Retrieve the wallet from the database.
        Expects the wallet document to include an "id" field.
        """
        wallet = await self.db.wallets.find_one({"id": wallet_id})
        return WalletDB(**wallet) if wallet else None

    async def create_agent_wallet(self, wallet_data: dict) -> dict:
        """
        Insert a new agent wallet into the database.
        wallet_data should be a dict with at least these keys:
          - agent_id: the unique identifier for the agent
          - wallet_address: the blockchain address of the wallet
          - private_key: the private key corresponding to the wallet
        """
        result = await self.db.wallets.insert_one(wallet_data)
        wallet_data["_id"] = str(result.inserted_id)
        return wallet_data

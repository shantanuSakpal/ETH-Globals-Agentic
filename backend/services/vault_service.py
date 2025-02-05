from typing import Optional, List, Dict, Any
from backend.core.agents.morpho.agent import MorphoAgent
from backend.core.manager.agent import AgentManager
from models.vault import Vault, VaultCreate, VaultStatus
from models.database import VaultDB
from services.database import DatabaseService
from core.manager.strategy import StrategyManager
from config.settings import get_settings
import logging
from cdp_agentkit_core.actions.morpho.deposit import MorphoDepositInput, deposit_to_morpho
from cdp import Wallet
from models.wallet import WalletDB
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class VaultService:
    def __init__(self):
        settings = get_settings()
        self.db = DatabaseService(settings.MONGODB_URL)
        self.strategy_manager = StrategyManager()
        self.agent_manager = AgentManager()

    async def create_user_wallet(self, user_id: str) -> Optional[WalletDB]:
        try:
            # Create CDP wallet
            cdp_wallet = Wallet.create()
            
            wallet = WalletDB(
                id=str(uuid.uuid4()),
                user_id=user_id,
                cdp_wallet_id=cdp_wallet.id,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            await self.db.create_wallet(wallet)
            return wallet
            
        except Exception as e:
            logger.error(f"Error creating user wallet: {str(e)}")
            return None

    async def create_vault(self, vault_create: VaultCreate) -> Optional[Vault]:
        try:
            # First ensure user has a wallet
            wallet = await self.db.get_user_wallet(vault_create.user_id)
            if not wallet:
                wallet = await self.create_user_wallet(vault_create.user_id)
                if not wallet:
                    raise Exception("Failed to create user wallet")

            # Create vault with wallet info
            vault = await self.strategy_manager.initialize_strategy(
                vault_create, 
                wallet.cdp_wallet_id
            )
            
            if not vault:
                raise Exception("Failed to initialize strategy for vault")

            # Create vault in database
            vault_db = VaultDB(
                id=vault.id,
                user_id=vault.user_id,
                strategy_id=vault.strategy_id,
                status=vault.status,
                initial_deposit=vault_create.initial_deposit,
                current_balance=vault_create.initial_deposit
            )
            
            await self.db.create_vault(vault_db)
            return vault

        except Exception as e:
            logger.error(f"Error creating vault: {str(e)}")
            return None

    async def get_vault(self, vault_id: str) -> Optional[Vault]:
        try:
            vault_db = await self.db.get_vault(vault_id)
            if not vault_db:
                return None

            return Vault(
                id=vault_db.id,
                user_id=vault_db.user_id,
                strategy_id=vault_db.strategy_id,
                status=VaultStatus(vault_db.status),
                balance=vault_db.current_balance,
                created_at=vault_db.created_at,
                updated_at=vault_db.updated_at
            )

        except Exception as e:
            logger.error(f"Error getting vault: {str(e)}")
            return None

    async def update_vault_balance(self, vault_id: str, new_balance: float) -> bool:
        try:
            await self.db.update_vault_balance(vault_id, new_balance)
            return True
        except Exception as e:
            logger.error(f"Error updating vault balance: {str(e)}")
            return False

    async def handle_deposit(
        self, 
        user_id: str, 
        vault_id: str,
        amount: float, 
        token: str,
        slippage: float = 0.01
    ) -> Dict[str, Any]:
        """Handle user deposit to CDP wallet and Morpho"""
        try:
            # Get user's wallet and vault
            wallet = await self.db.get_user_wallet(user_id)
            if not wallet:
                raise Exception("User wallet not found")
            
            vault = await self.get_vault(vault_id)
            if not vault:
                raise Exception("Vault not found")
            
            agent = self.agent_manager.get_agent(vault.id)
            
            # Execute deposit through CDP wallet
            deposit_result = await agent.execute_deposit({
                "token_address": token,
                "amount": amount,
                "wallet_id": wallet.cdp_wallet_id,
                "slippage": slippage
            })
            
            # Update vault balance
            new_balance = vault.balance + amount
            await self.update_vault_balance(vault.id, new_balance)
            
            return {
                "status": "success",
                "tx_hash": deposit_result["tx_hash"],
                "new_balance": new_balance
            }
        except Exception as e:
            raise Exception(f"Deposit flow failed: {str(e)}")

from typing import Optional, List, Dict, Any
from core.agents.morpho.agent import MorphoAgent
from core.manager.agent import AgentManager
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
from models.websocket import WSMessage, WSMessageType
import os
import asyncio
from utils.vault_factory import VaultFactoryClient

logger = logging.getLogger(__name__)

class VaultService:
    def __init__(self, manager=None):
        settings = get_settings()
        self.db = DatabaseService(settings.MONGODB_URL)
        self.strategy_manager = StrategyManager(self.agent_manager)
        self.agent_manager = AgentManager()
        self.manager = manager  # Connection manager instance

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
            # Update balance in database
            await self.db.update_vault_balance(vault_id, new_balance)
            
            # Create WebSocket message
            message = WSMessage(
                type=WSMessageType.BALANCE_UPDATE,
                data={
                    "vault_id": vault_id,
                    "new_balance": new_balance,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Broadcast to subscribed clients
            if self.manager:
                await self.manager.broadcast_message(
                    message=message,
                    topic=f"vault_{vault_id}"  # Topic for this vault
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating vault balance: {str(e)}")
            return False

    async def handle_deposit(self, user_id: str, vault_id: str, amount: float, token: str, slippage: float = 0.01) -> dict:
        """Handle user deposit to CDP wallet and Morpho, deploying the vault contract if needed."""
        try:
            wallet = await self.db.get_user_wallet(user_id)
            if not wallet:
                raise Exception("User wallet not found")

            vault = await self.get_vault(vault_id)
            if not vault:
                raise Exception("Vault not found")

            agent = self.agent_manager.get_agent(vault.id)
            if not agent:
                raise Exception("Agent not found")

            # If vault contract not deployed, deploy it.
            deposit_address = vault.settings.get("deposit_address") if vault.settings else None
            if not deposit_address:
                # Retrieve addresses: assume agent.wallet_data contains agent's wallet address,
                # and the user's CDP wallet ID is in wallet.cdp_wallet_id.
                agent_wallet_address = agent.strategy_params.get("wallet_data", {}).get("address")
                user_wallet_address = wallet.cdp_wallet_id
                if not agent_wallet_address or not user_wallet_address:
                    raise Exception("Missing wallet addresses for deployment")
                deposit_address = await self.deploy_vault_contract(vault, agent_wallet_address, user_wallet_address)

            # Now execute deposit through the agent.
            deposit_result = await agent.execute_deposit({
                "token_address": token,
                "amount": amount,
                "wallet_id": wallet.cdp_wallet_id,
                "slippage": slippage,
                "vault_address": deposit_address  # Pass vault contract address to the deposit action
            })

            # Update vault balance.
            new_balance = vault.balance + amount
            await self.update_vault_balance(vault.id, new_balance)

            return {
                "status": "success",
                "tx_hash": deposit_result.get("tx_hash"),
                "new_balance": new_balance
            }
        except Exception as e:
            raise Exception(f"Deposit flow failed: {str(e)}")

    async def deploy_vault_contract(self, vault, agent_wallet_address, user_wallet_address) -> str:
        """
        Deploy the vault contract using the VaultFactory.
        Update the vault record with the deployed contract address.
        """
        try:
            rpc_url = os.environ.get("RPC_URL")
            factory_address = os.environ.get("VAULT_FACTORY_ADDRESS")
            deployer_private_key = os.environ.get("DEPLOYER_PRIVATE_KEY")
            client = VaultFactoryClient(rpc_url, factory_address, deployer_private_key)
            # Wrap the synchronous call in asyncio.to_thread
            vault_contract_address = await asyncio.to_thread(
                client.deploy_vault, agent_wallet_address, user_wallet_address
            )
            # Update vault settings with the deployed contract address
            if not hasattr(vault, "settings") or vault.settings is None:
                vault.settings = {}
            vault.settings["deposit_address"] = vault_contract_address

            # Persist the updated vault record to the database (pseudo-code)
            await self.db.update_vault_settings(vault.id, vault.settings)
            logger.info(f"Vault contract deployed at {vault_contract_address} for vault {vault.id}")
            return vault_contract_address
        except Exception as e:
            logger.error(f"Vault deployment error: {str(e)}")
            raise

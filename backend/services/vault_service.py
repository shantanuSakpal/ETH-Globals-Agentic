import os
import asyncio
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from models.database import VaultDB
from config.settings import get_settings
from services.database import DatabaseService
from core.manager.strategy import StrategyManager
from core.manager.agent import AgentManager
from models.vault import Vault, VaultCreate, VaultStatus
from models.wallet import WalletDB
from cdp_agentkit_core.actions.morpho.deposit import MorphoDepositInput
from cdp import Wallet
from models.websocket import WSMessage, WSMessageType
from utils.vault_factory import VaultFactoryClient
from web3 import Web3

logger = logging.getLogger(__name__)

class VaultService:
    def __init__(self, manager=None):
        settings = get_settings()
        self.db = DatabaseService(settings.MONGODB_URL)
        self.agent_manager = AgentManager()
        self.strategy_manager = StrategyManager(self.agent_manager)
        self.manager = manager  # Connection manager instance

        #         # Load required environment variables:
        # rpc_url = os.environ.get("WEB3_PROVIDER_URI")
        # factory_address = os.environ.get("VAULT_FACTORY_ADDRESS")
        # deployer_private_key = os.environ.get("CDP_API_KEY_PRIVATE_KEY")

        # Load required environment variables from settings
        rpc_url = settings.WEB3_PROVIDER_URI
        factory_address = settings.VAULT_FACTORY_ADDRESS
        deployer_private_key = settings.DEPLOYER_PRIVATE_KEY
        
        if not rpc_url or not factory_address or not deployer_private_key:
            raise Exception("Missing required environment variables for VaultFactory deployment")
        
        # Initialize the VaultFactoryClient using settings
        self.factory_client = VaultFactoryClient(rpc_url, factory_address, deployer_private_key)

    async def create_vault(self, data: Dict[str, Any], user_id: str) -> Optional[Vault]:
        # Create a vault record (implementation placeholder)
        try:
            vault_id = str(uuid.uuid4())
            vault = Vault(
                id=vault_id,
                strategy_id=data["strategy_id"],
                balance=data.get("initial_deposit", 0),
                status=VaultStatus.PENDING,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                settings={},
                user_id=user_id
            )
            # Persist the vault record in the DB (pseudo-code)
            await self.db.create_vault(vault)
            return vault
        except Exception as e:
            logger.error(f"Failed to create vault: {str(e)}")
            return None

    async def handle_deposit(self, user_id: str, vault_id: str, amount: float, token: str, user_wallet_address: str, slippage: float = 0.01) -> Dict[str, Any]:
        """Handle user deposit to CDP wallet and Morpho, deploying the vault contract if needed."""
        try:
            wallet = await self.db.get_agent_wallet(user_id)
            if not wallet:
                raise Exception("Agent wallet not found")

            vault = await self.db.get_vault(vault_id)
            if not vault:
                raise Exception("Vault not found")

            agent = self.agent_manager.get_agent(vault.id)
            if not agent:
                raise Exception("Agent not found")

            # Optionally validate user_wallet_address here
            if not user_wallet_address:
                raise Exception("User wallet address must be provided")

            # If vault contract not deployed, deploy it.
            deposit_address = vault.settings.get("deposit_address") if vault.settings else None
            if not deposit_address:
                agent_wallet_address = agent.strategy_params.get("wallet_data", {}).get("address")
                if not agent_wallet_address or not user_wallet_address:
                    raise Exception("Missing wallet addresses for deployment")
                deposit_address = await self.deploy_vault_contract(vault, agent_wallet_address, user_wallet_address)

            # Prepare deposit input parameters (include vault contract address)
            deposit_input = {
                "token_address": token,
                "amount": amount,
                "wallet_id": wallet.cdp_wallet_id,
                "slippage": slippage,
                "vault_address": deposit_address
            }

            # Execute deposit action through the agent
            deposit_result = await agent.execute_deposit(deposit_input)

            # Update vault balance (assuming vault has an attribute "balance")
            new_balance = vault.current_balance + amount
            vault.current_balance = new_balance
            await self.db.update_vault_balance(vault.id, new_balance)

            return {
                "status": "success",
                "tx_hash": deposit_result.get("tx_hash"),
                "new_balance": new_balance
            }
        except Exception as e:
            logger.error(f"Deposit flow failed: {str(e)}")
            raise Exception(f"Deposit flow failed: {str(e)}")

    async def deploy_vault_contract(self, vault: Vault, agent_wallet_address: str, user_wallet_address: str) -> str:
        """
        Deploy the vault contract using the VaultFactoryClient.
        Update the vault record with the deployed contract address.
        """
        try:
            # Run the blocking deployment code in a different thread to avoid blocking the event loop.
            loop = asyncio.get_event_loop()
            vault_contract_address = await loop.run_in_executor(
                None,
                self.factory_client.deploy_vault,
                agent_wallet_address,
                user_wallet_address
            )
            if not hasattr(vault, "settings") or vault.settings is None:
                vault.settings = {}
            vault.settings["deposit_address"] = vault_contract_address
            # Persist the updated vault record to the database
            await self.db.update_vault_settings(vault.id, vault.settings)
            logger.info(f"Vault contract deployed at {vault_contract_address} for vault {vault.id}")
            return vault_contract_address
        except Exception as e:
            logger.error(f"Vault deployment error: {str(e)}")
            raise
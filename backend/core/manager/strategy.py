from datetime import datetime
from typing import Dict, Any, Optional
import uuid
from models.vault import Vault, VaultCreate, VaultStatus
from .agent import AgentManager
import logging

class StrategyManager:
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
        self.vaults: Dict[str, Vault] = {}
        self.logger = logging.getLogger(__name__)

    async def initialize_strategy(
        self, 
        vault_create: VaultCreate,
        cdp_wallet_id: str
    ) -> Optional[Vault]:
        try:
            # Create vault
            vault = Vault(
                **vault_create.model_dump(),
                id=str(uuid.uuid4()),
                status=VaultStatus.PENDING,
                balance=vault_create.initial_deposit,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Initialize agent with wallet
            success = await self.agent_manager.add_agent(
                agent_id=vault.id,
                strategy_params={
                    "vault_id": vault.id,
                    "strategy_id": vault_create.strategy_id,
                    "initial_deposit": vault_create.initial_deposit,
                    "cdp_wallet_id": cdp_wallet_id
                }
            )

            if success:
                vault.status = VaultStatus.ACTIVE
                self.vaults[vault.id] = vault
                print(f"Creating vault with balance: {vault_create.initial_deposit}")
                print(f"Vault created: {vars(vault)}")
                return vault
                
            return None
            # else:
            #     await self.db.delete_vault(vault.id)  # If using DB
            #     return None
        
        except Exception as e:
            self.logger.error(f"Error initializing strategy: {str(e)}")
            return None

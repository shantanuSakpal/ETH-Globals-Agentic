from typing import Dict, Any
from models.websocket import WSMessageType, WSMessage
from services.vault_service import VaultService
from core.manager.agent import AgentManager
#from core.manager.strategy_monitor import StrategyMonitor
from services.monitor import StrategyMonitor
import logging

logger = logging.getLogger(__name__)

class WebSocketService:
    """
        WebSocket Business Logic Service

        Implements the business logic for WebSocket message handling, particularly
        for strategy initialization and monitoring.

        Responsibilities:
            - Strategy selection processing
            - Vault creation and management
            - Agent initialization
            - Monitoring setup
            - Deposit handling

        Example:
            service = WebSocketService(vault_service, agent_manager, monitor)
            response = await service.process_strategy_selection(data, user_id)
    """
    def __init__(self, vault_service: VaultService, agent_manager: AgentManager, monitor: StrategyMonitor):
        self.vault_service = vault_service
        self.agent_manager = agent_manager
        self.monitor = monitor

    async def handle_message(self, message_type: str, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Main message handler that routes to specific handlers"""
        try:
            if message_type == "strategy_select":
                return await self.process_strategy_selection(data, user_id)
            elif message_type == "deposit":
                return await self.process_deposit(data, user_id)
            else:
                return {
                    "type": "error",
                    "data": {"message": f"Unknown message type: {message_type}"}
                }
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            return {"type": "error", "data": {"message": str(e)}}

    async def process_strategy_selection(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        try:
            # Step 1: Create vault and initialize strategy; this creates the vault record.
            vault = await self.vault_service.create_vault(data, user_id)
            if not vault:
                raise Exception("Failed to create vault")
            
            # Step 2: Ensure agent wallet data is available.
            # If not provided by the client, create one using WalletService.
            wallet_data = data.get("agent_wallet_data")
            if not wallet_data:
                from services.wallet_service import WalletService
                wallet_service = WalletService()
                wallet_data = await wallet_service.create_agent_wallet(user_id)
            
            # Step 3: Initialize agent with wallet data.
            success = await self.agent_manager.add_agent(
                agent_id=vault.id,
                strategy_params={
                    "vault_id": vault.id,
                    "strategy_id": data["strategy_id"],
                    "initial_deposit": data.get("initial_deposit", 0),
                    "parameters": data.get("parameters", {}),
                    "wallet_data": wallet_data
                }
            )
            
            if not success:
                raise Exception("Failed to initialize agent")
            
            # Step 4: Start monitoring for this vault.
            await self.monitor.start_monitoring(vault.id)
            
            # Return instructions to the frontend:
            # The returned deposit_address may be None at this point.
            response_data = {
                "vault_id": vault.id,
                "status": "initialized",
                "deposit_address": vault.settings.get("deposit_address") if vault.settings else None,
                "message": "Strategy initialized successfully. Please fund the agent wallet with gas to continue."
            }
            return {
                "type": WSMessageType.STRATEGY_INIT,
                "data": response_data
            }
        except Exception as e:
            logger.error(f"Strategy selection error: {str(e)}")
            return {
                "type": WSMessageType.ERROR,
                "data": {"message": str(e)}
            }

    async def process_deposit(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process deposit business logic which will check for vault deployment if needed."""
        result = await self.vault_service.handle_deposit(
            user_id=user_id,
            vault_id=data["vault_id"],
            amount=data["amount"],
            token=data["token_address"],
            slippage=data.get("slippage", 0.01)
        )
        return {
            "type": "deposit_complete",
            "data": result
        }

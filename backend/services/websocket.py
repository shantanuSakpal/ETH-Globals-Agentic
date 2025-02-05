from typing import Dict, Any
from models.websocket import WSMessageType
from services.vault_service import VaultService
from core.manager.agent import AgentManager
import logging

logger = logging.getLogger(__name__)

class WebSocketService:
    def __init__(self, vault_service: VaultService, agent_manager: AgentManager):
        self.vault_service = vault_service
        self.agent_manager = agent_manager

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
        """Process strategy selection business logic"""
        vault = await self.vault_service.create_vault(data, user_id)
        if not vault:
            raise Exception("Failed to create vault")
            
        return {
            "type": "strategy_initialized",
            "data": {
                "vault_id": vault.id,
                "status": vault.status,
                "deposit_address": vault.settings.get("deposit_address")
            }
        }

    async def process_deposit(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process deposit business logic"""
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

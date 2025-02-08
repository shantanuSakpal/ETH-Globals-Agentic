import os
import httpx
import logging

logger = logging.getLogger(__name__)

class WalletService:
    def __init__(self):
        # Base URL for Coinbase Developer Managed Wallets.
        self.api_url = os.environ.get("COINBASE_WALLET_API_URL", "https://api.cdp.coinbase.com/v2/wallets")
        self.api_key = os.environ.get("COINBASE_WALLET_API_KEY")
        self.api_secret = os.environ.get("COINBASE_WALLET_API_SECRET")
        
    async def create_agent_wallet(self, user_id: str) -> dict:
        """
        Create a new agent wallet using Coinbase's Developer Managed Wallet API.
        
        Args:
            user_id (str): Identifier for the owner of the wallet.
        
        Returns:
            dict: Wallet data containing the wallet id, address, etc.
        """
        headers = {
            "Content-Type": "application/json",
            "CB-ACCESS-KEY": self.api_key,
            # Additional headers (e.g., signatures) may be needed.
        }
        payload = {
            "user_id": user_id,
            # Additional parameters as required by the Coinbase API.
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, json=payload, headers=headers)
            if response.status_code == 201:
                data = response.json()
                wallet_info = data.get("data")
                logger.info("Agent wallet created successfully.")
                return wallet_info
            else:
                logger.error(f"Failed to create wallet: {response.text}")
                raise Exception("Wallet creation failed") 
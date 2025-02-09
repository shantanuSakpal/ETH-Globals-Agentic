import os
import uuid
import logging
from datetime import datetime
from config.settings import get_settings
from services.database import DatabaseService
from models.wallet import Wallet as WalletModel, WalletDB
from cdp import Cdp, Wallet

logger = logging.getLogger(__name__)

class WalletService:
    def __init__(self):
        # Get CDP credentials from environment variables
        settings = get_settings()
        self.api_key_name = settings.CDP_API_KEY_NAME
        self.api_key_private_key = settings.CDP_API_KEY_PRIVATE_KEY
        
        if not self.api_key_name or not self.api_key_private_key:
            raise ValueError("CDP API credentials not properly configured in environment variables")
        
        # Configure CDP SDK
        try:
            Cdp.configure(self.api_key_name, self.api_key_private_key)
            logger.info("CDP SDK has been successfully configured with CDP API key")
        except Exception as e:
            logger.error(f"Failed to configure CDP SDK: {str(e)}")
            raise
            
        self.network_id = settings.NETWORK_ID
        self.db = DatabaseService(settings.MONGODB_URL)
        #self.wallet = None

    async def create_agent_wallet(self, user_id: str) -> WalletModel:
        """
        Create a new agent wallet using CDP's Wallet API,
        persist the wallet details using the WalletDB model,
        and return a Wallet domain model.
        
        Args:
            user_id (str): Identifier for the owner of the wallet.
        
        Returns:
            WalletModel: The created wallet as a domain model.
        """
        try:
            logger.info(f"Creating wallet for user: {user_id}")
            logger.info(f"Network ID: {self.network_id}")
            
            # Create wallet using CDP SDK
            wallet = Wallet.create(self.network_id)
            logger.info(f"Wallet created: {wallet}")
            
            # Export the wallet data
            wallet_data = wallet.export_data()
            logger.info("Agent wallet created successfully from API.")
            
            now = datetime.now()
            # Create the persistence model instance
            wallet_db = WalletDB(
                id=str(uuid.uuid4()),
                user_id=user_id,
                cdp_wallet_id=str(wallet_data.get("id")),  # External wallet ID from CDP
                address=str(wallet_data.get("address")),    # Wallet address
                created_at=now,
                updated_at=now,
                status="active",
                wallet_data=wallet_data  # Store the complete wallet data
            )
            
            # Persist the wallet in the database.
            await self.db.create_agent_wallet(wallet_db)
            logger.info("Agent wallet persisted in the database.")
            
            # Create and return the domain model instance.
            wallet = WalletModel(
                id=wallet_db.id,
                user_id=wallet_db.user_id,
                address=wallet_db.address,
                status=wallet_db.status,
                created_at=wallet_db.created_at,
                updated_at=wallet_db.updated_at
            )
            return wallet

        except Exception as e:
            logger.error(f"Failed to create wallet: {str(e)}")
            raise Exception("Wallet creation failed")
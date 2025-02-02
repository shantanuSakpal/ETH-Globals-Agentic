from typing import Dict, Any, Optional
from web3 import Web3
import json
import logging
from eth_typing import Address
from web3.contract import Contract
import asyncio

logger = logging.getLogger(__name__)

class MorphoClient:
    """
    Client for interacting with the Morpho protocol.
    Handles all protocol-specific operations including lending, borrowing, and position management.
    """
    
    def __init__(self, web3_provider: str, contract_address: str):
        """
        Initialize the Morpho client
        
        Args:
            web3_provider: URL of the Web3 provider
            contract_address: Address of the Morpho protocol contract
        """
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
        self.contract_address = Web3.to_checksum_address(contract_address)
        self.contract = None
        self.markets_cache = {}
        self.last_update = 0
        
    async def validate_connection(self) -> bool:
        """
        Validate connection to the Morpho protocol
        
        Returns:
            bool: True if connection is valid, False otherwise
        """
        try:
            # Load contract ABI and create contract instance
            # In a real implementation, load ABI from file or external source
            abi = []  # Add actual Morpho ABI here
            self.contract = self.w3.eth.contract(
                address=self.contract_address,
                abi=abi
            )
            
            # Test connection by calling a view function
            await self._call_contract_method("getMarketsData")
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate Morpho connection: {str(e)}")
            return False
            
    async def get_markets_data(self) -> Dict[str, Any]:
        """
        Get current market data from Morpho protocol
        
        Returns:
            Dict containing market data
        """
        try:
            markets_data = await self._call_contract_method("getMarketsData")
            self.markets_cache = self._process_markets_data(markets_data)
            self.last_update = self.w3.eth.get_block('latest').timestamp
            return self.markets_cache
            
        except Exception as e:
            logger.error(f"Error fetching markets data: {str(e)}")
            raise
            
    async def get_position(self, position_id: str) -> Dict[str, Any]:
        """
        Get details of a specific position
        
        Args:
            position_id: ID of the position
            
        Returns:
            Dict containing position details
        """
        try:
            position = await self._call_contract_method(
                "getPosition",
                position_id
            )
            return self._process_position_data(position)
            
        except Exception as e:
            logger.error(f"Error fetching position {position_id}: {str(e)}")
            raise
            
    async def open_position(
        self,
        size: float,
        leverage: float,
        position_type: str
    ) -> bool:
        """
        Open a new position
        
        Args:
            size: Size of the position
            leverage: Leverage ratio
            position_type: Type of position (long/short)
            
        Returns:
            bool: True if position was opened successfully
        """
        try:
            # Convert parameters to contract format
            size_wei = self.w3.to_wei(size, 'ether')
            leverage_scaled = int(leverage * 1e18)
            
            # Build transaction
            tx = await self._build_transaction(
                "openPosition",
                size_wei,
                leverage_scaled,
                position_type
            )
            
            # Send transaction
            tx_hash = await self._send_transaction(tx)
            
            # Wait for confirmation
            receipt = await self._wait_for_transaction(tx_hash)
            return receipt.status == 1
            
        except Exception as e:
            logger.error(f"Error opening position: {str(e)}")
            raise
            
    async def close_position(self, position_id: str) -> bool:
        """
        Close an existing position
        
        Args:
            position_id: ID of the position to close
            
        Returns:
            bool: True if position was closed successfully
        """
        try:
            tx = await self._build_transaction(
                "closePosition",
                position_id
            )
            
            tx_hash = await self._send_transaction(tx)
            receipt = await self._wait_for_transaction(tx_hash)
            return receipt.status == 1
            
        except Exception as e:
            logger.error(f"Error closing position {position_id}: {str(e)}")
            raise
            
    async def adjust_position(
        self,
        position_id: str,
        size_delta: float
    ) -> bool:
        """
        Adjust the size of an existing position
        
        Args:
            position_id: ID of the position to adjust
            size_delta: Change in position size (positive for increase, negative for decrease)
            
        Returns:
            bool: True if position was adjusted successfully
        """
        try:
            size_delta_wei = self.w3.to_wei(abs(size_delta), 'ether')
            
            if size_delta > 0:
                method = "increasePosition"
            else:
                method = "decreasePosition"
                
            tx = await self._build_transaction(
                method,
                position_id,
                size_delta_wei
            )
            
            tx_hash = await self._send_transaction(tx)
            receipt = await self._wait_for_transaction(tx_hash)
            return receipt.status == 1
            
        except Exception as e:
            logger.error(f"Error adjusting position {position_id}: {str(e)}")
            raise
            
    async def get_account_data(self, address: str) -> Dict[str, Any]:
        """
        Get account data from Morpho protocol
        
        Args:
            address: Address to get data for
            
        Returns:
            Dict containing account data
        """
        try:
            account_data = await self._call_contract_method(
                "getAccountData",
                Web3.to_checksum_address(address)
            )
            return self._process_account_data(account_data)
            
        except Exception as e:
            logger.error(f"Error fetching account data for {address}: {str(e)}")
            raise
            
    async def _call_contract_method(self, method: str, *args) -> Any:
        """
        Call a contract method
        
        Args:
            method: Name of the method to call
            *args: Arguments to pass to the method
            
        Returns:
            Result of the contract call
        """
        try:
            contract_method = getattr(self.contract.functions, method)
            return await contract_method(*args).call()
            
        except Exception as e:
            logger.error(f"Error calling contract method {method}: {str(e)}")
            raise
            
    async def _build_transaction(self, method: str, *args) -> Dict[str, Any]:
        """
        Build a transaction for a contract method
        
        Args:
            method: Name of the method
            *args: Arguments to pass to the method
            
        Returns:
            Dict containing transaction data
        """
        try:
            contract_method = getattr(self.contract.functions, method)
            return contract_method(*args).build_transaction({
                'from': self.w3.eth.default_account,
                'nonce': await self.w3.eth.get_transaction_count(
                    self.w3.eth.default_account
                )
            })
            
        except Exception as e:
            logger.error(f"Error building transaction for {method}: {str(e)}")
            raise
            
    async def _send_transaction(self, transaction: Dict[str, Any]) -> str:
        """
        Send a transaction
        
        Args:
            transaction: Transaction to send
            
        Returns:
            str: Transaction hash
        """
        try:
            signed_tx = self.w3.eth.account.sign_transaction(
                transaction,
                self.private_key
            )
            return await self.w3.eth.send_raw_transaction(
                signed_tx.rawTransaction
            )
            
        except Exception as e:
            logger.error(f"Error sending transaction: {str(e)}")
            raise
            
    async def _wait_for_transaction(self, tx_hash: str) -> Any:
        """
        Wait for a transaction to be mined
        
        Args:
            tx_hash: Hash of the transaction
            
        Returns:
            Transaction receipt
        """
        while True:
            try:
                receipt = await self.w3.eth.get_transaction_receipt(tx_hash)
                if receipt is not None:
                    return receipt
            except Exception as e:
                logger.error(f"Error getting transaction receipt: {str(e)}")
                raise
            await asyncio.sleep(1)
            
    def _process_markets_data(self, raw_data: Any) -> Dict[str, Any]:
        """Process raw markets data into a more usable format"""
        # Implement data processing logic
        return {}
        
    def _process_position_data(self, raw_data: Any) -> Dict[str, Any]:
        """Process raw position data into a more usable format"""
        # Implement data processing logic
        return {}
        
    def _process_account_data(self, raw_data: Any) -> Dict[str, Any]:
        """Process raw account data into a more usable format"""
        # Implement data processing logic
        return {} 
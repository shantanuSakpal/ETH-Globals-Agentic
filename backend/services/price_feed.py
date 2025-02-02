from typing import Dict, Any, Optional
import aiohttp
import logging
import json
from datetime import datetime, timedelta
import asyncio
from config.settings import get_settings

logger = logging.getLogger(__name__)

class PriceFeed:
    """
    Service for fetching real-time and historical price data from various sources.
    Supports multiple price feeds and aggregation strategies.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the price feed service
        
        Args:
            api_key: Optional API key for premium data sources
        """
        self.api_key = api_key
        self.settings = get_settings()
        self.cache = {}
        self.last_update = {}
        self.update_interval = 60  # seconds
        self.session = None
        
    async def validate_connection(self) -> bool:
        """
        Validate connection to price feed services
        
        Returns:
            bool: True if connection is valid
        """
        try:
            self.session = aiohttp.ClientSession()
            # Test connection by fetching ETH price
            await self.get_price("ETH-USD")
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate price feed connection: {str(e)}")
            return False
            
    async def get_price(self, symbol: str) -> float:
        """
        Get current price for a symbol
        
        Args:
            symbol: Trading pair symbol (e.g., 'ETH-USD')
            
        Returns:
            float: Current price
        """
        try:
            market_data = await self.get_market_data(symbol)
            return float(market_data["price"])
            
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {str(e)}")
            raise
            
    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive market data for a symbol
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Dict containing market data
        """
        try:
            # Check cache first
            if self._should_update(symbol):
                data = await self._fetch_market_data(symbol)
                self._update_cache(symbol, data)
            return self.cache[symbol]
            
        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {str(e)}")
            raise
            
    async def get_historical_data(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        interval: str = "1h"
    ) -> list:
        """
        Get historical price data
        
        Args:
            symbol: Trading pair symbol
            start_time: Start time for historical data
            end_time: End time for historical data
            interval: Time interval for data points
            
        Returns:
            List of historical data points
        """
        try:
            # Implement historical data fetching logic
            return await self._fetch_historical_data(
                symbol,
                start_time,
                end_time,
                interval
            )
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            raise
            
    async def get_aggregated_price(
        self,
        symbol: str,
        sources: list = None
    ) -> float:
        """
        Get price aggregated from multiple sources
        
        Args:
            symbol: Trading pair symbol
            sources: List of price sources to use
            
        Returns:
            float: Aggregated price
        """
        try:
            if sources is None:
                sources = ["coinbase", "binance", "kraken"]
                
            prices = await asyncio.gather(*[
                self._fetch_price_from_source(symbol, source)
                for source in sources
            ])
            
            # Remove None values
            valid_prices = [p for p in prices if p is not None]
            
            if not valid_prices:
                raise ValueError(f"No valid prices found for {symbol}")
                
            # Calculate median price
            valid_prices.sort()
            mid = len(valid_prices) // 2
            if len(valid_prices) % 2 == 0:
                return (valid_prices[mid-1] + valid_prices[mid]) / 2
            return valid_prices[mid]
            
        except Exception as e:
            logger.error(f"Error fetching aggregated price for {symbol}: {str(e)}")
            raise
            
    def _should_update(self, symbol: str) -> bool:
        """Check if cache should be updated"""
        if symbol not in self.last_update:
            return True
            
        elapsed = datetime.now() - self.last_update[symbol]
        return elapsed.total_seconds() > self.update_interval
        
    def _update_cache(self, symbol: str, data: Dict[str, Any]):
        """Update cache with new data"""
        self.cache[symbol] = data
        self.last_update[symbol] = datetime.now()
        
    async def _fetch_market_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch market data from primary source"""
        # Implementation will depend on chosen price feed API
        # This is a placeholder implementation
        async with self.session.get(
            f"https://api.example.com/v1/market-data/{symbol}",
            headers={"Authorization": f"Bearer {self.api_key}"}
        ) as response:
            if response.status != 200:
                raise Exception(f"API request failed: {await response.text()}")
            return await response.json()
            
    async def _fetch_historical_data(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        interval: str
    ) -> list:
        """Fetch historical data from source"""
        # Implementation will depend on chosen price feed API
        params = {
            "symbol": symbol,
            "start": int(start_time.timestamp()),
            "end": int(end_time.timestamp()),
            "interval": interval
        }
        
        async with self.session.get(
            "https://api.example.com/v1/historical",
            params=params,
            headers={"Authorization": f"Bearer {self.api_key}"}
        ) as response:
            if response.status != 200:
                raise Exception(f"API request failed: {await response.text()}")
            return await response.json()
            
    async def _fetch_price_from_source(
        self,
        symbol: str,
        source: str
    ) -> Optional[float]:
        """Fetch price from a specific source"""
        try:
            # Implementation will depend on chosen price sources
            # This is a placeholder implementation
            async with self.session.get(
                f"https://api.{source}.com/v1/price/{symbol}"
            ) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                return float(data["price"])
                
        except Exception as e:
            logger.warning(f"Error fetching price from {source}: {str(e)}")
            return None
            
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close() 
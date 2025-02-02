from typing import Dict, Any, Optional
import logging
from services.morpho_client import MorphoClient
from services.price_feed import PriceFeed
from config.settings import get_settings
import asyncio

logger = logging.getLogger(__name__)

class ETHLoopStrategy:
    """
    ETH-USDC Loop Strategy using Morpho protocol.
    Implements a leveraged yield farming strategy by looping between ETH and USDC.
    """
    
    def __init__(
        self,
        morpho_client: MorphoClient,
        price_feed: PriceFeed,
        params: Dict[str, Any]
    ):
        """
        Initialize the strategy
        
        Args:
            morpho_client: Morpho protocol client
            price_feed: Price feed service
            params: Strategy parameters
        """
        self.morpho_client = morpho_client
        self.price_feed = price_feed
        self.settings = get_settings()
        
        # Strategy parameters
        self.max_leverage = params.get("max_leverage", 3.0)
        self.min_collateral_ratio = params.get("min_collateral_ratio", 1.5)
        self.target_apy = params.get("target_apy", 10.0)
        self.rebalance_threshold = params.get("rebalance_threshold", 5.0)
        self.position_size = params.get("position_size", 0.0)
        
        # Strategy state
        self.current_position = None
        self.last_rebalance = None
        self.performance_metrics = {}
        
    async def initialize(self) -> bool:
        """
        Initialize the strategy
        
        Returns:
            bool: True if initialization was successful
        """
        try:
            # Validate initial conditions
            eth_price = await self.price_feed.get_price("ETH-USD")
            markets = await self.morpho_client.get_markets_data()
            
            # Check if markets are healthy
            if not self._validate_markets(markets):
                logger.error("Markets validation failed")
                return False
                
            # Initialize performance tracking
            self.performance_metrics = {
                "entry_price": eth_price,
                "current_price": eth_price,
                "pnl": 0.0,
                "apy": 0.0,
                "leverage": 1.0
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Strategy initialization failed: {str(e)}")
            return False
            
    async def execute(self) -> Dict[str, Any]:
        """
        Execute one iteration of the strategy
        
        Returns:
            Dict containing execution results
        """
        try:
            # Get current market state
            market_state = await self._get_market_state()
            
            # Check if rebalancing is needed
            if self._should_rebalance(market_state):
                await self._rebalance_position(market_state)
                
            # Update performance metrics
            await self._update_metrics(market_state)
            
            return {
                "success": True,
                "action": "rebalance" if self._should_rebalance(market_state) else "hold",
                "metrics": self.performance_metrics
            }
            
        except Exception as e:
            logger.error(f"Strategy execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def _get_market_state(self) -> Dict[str, Any]:
        """Get current market state"""
        try:
            eth_price = await self.price_feed.get_price("ETH-USD")
            markets = await self.morpho_client.get_markets_data()
            
            return {
                "eth_price": eth_price,
                "markets": markets,
                "timestamp": self.price_feed.last_update.get("ETH-USD")
            }
            
        except Exception as e:
            logger.error(f"Error getting market state: {str(e)}")
            raise
            
    def _should_rebalance(self, market_state: Dict[str, Any]) -> bool:
        """Determine if position should be rebalanced"""
        try:
            if not self.current_position:
                return False
                
            # Calculate price change since last rebalance
            price_change = abs(
                (market_state["eth_price"] - self.current_position["entry_price"])
                / self.current_position["entry_price"]
                * 100
            )
            
            return price_change >= self.rebalance_threshold
            
        except Exception as e:
            logger.error(f"Error checking rebalance condition: {str(e)}")
            return False
            
    async def _rebalance_position(self, market_state: Dict[str, Any]):
        """Rebalance the current position"""
        try:
            if not self.current_position:
                # Open new position
                size = self._calculate_position_size(market_state)
                leverage = self._calculate_leverage(market_state)
                
                success = await self.morpho_client.open_position(
                    size=size,
                    leverage=leverage,
                    position_type="long"
                )
                
                if success:
                    self.current_position = {
                        "size": size,
                        "leverage": leverage,
                        "entry_price": market_state["eth_price"]
                    }
            else:
                # Adjust existing position
                new_size = self._calculate_position_size(market_state)
                size_delta = new_size - self.current_position["size"]
                
                if abs(size_delta) > 0:
                    success = await self.morpho_client.adjust_position(
                        position_id=self.current_position["id"],
                        size_delta=size_delta
                    )
                    
                    if success:
                        self.current_position["size"] = new_size
                        
        except Exception as e:
            logger.error(f"Error rebalancing position: {str(e)}")
            raise
            
    def _calculate_position_size(self, market_state: Dict[str, Any]) -> float:
        """Calculate optimal position size"""
        try:
            eth_price = market_state["eth_price"]
            # Implement position sizing logic
            return self.position_size
            
        except Exception as e:
            logger.error(f"Error calculating position size: {str(e)}")
            return 0.0
            
    def _calculate_leverage(self, market_state: Dict[str, Any]) -> float:
        """Calculate optimal leverage"""
        try:
            # Implement leverage calculation logic
            return min(
                self.max_leverage,
                market_state["markets"]["eth"]["max_leverage"]
            )
            
        except Exception as e:
            logger.error(f"Error calculating leverage: {str(e)}")
            return 1.0
            
    def _validate_markets(self, markets: Dict[str, Any]) -> bool:
        """Validate market conditions"""
        try:
            # Implement market validation logic
            return True
            
        except Exception as e:
            logger.error(f"Error validating markets: {str(e)}")
            return False
            
    async def _update_metrics(self, market_state: Dict[str, Any]):
        """Update strategy performance metrics"""
        try:
            if self.current_position:
                entry_price = self.current_position["entry_price"]
                current_price = market_state["eth_price"]
                
                # Calculate PnL
                pnl_pct = (current_price - entry_price) / entry_price * 100
                leveraged_pnl = pnl_pct * self.current_position["leverage"]
                
                self.performance_metrics.update({
                    "current_price": current_price,
                    "pnl": leveraged_pnl,
                    "leverage": self.current_position["leverage"],
                    "position_size": self.current_position["size"]
                })
                
        except Exception as e:
            logger.error(f"Error updating metrics: {str(e)}")
            
    async def close(self):
        """Clean up strategy resources"""
        try:
            if self.current_position:
                await self.morpho_client.close_position(
                    self.current_position["id"]
                )
            self.current_position = None
            
        except Exception as e:
            logger.error(f"Error closing strategy: {str(e)}")
            raise 
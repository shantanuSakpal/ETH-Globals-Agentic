from typing import Dict, Any, Optional, List
from decimal import Decimal
import logging
from datetime import datetime, timedelta
from cdp_langchain.utils import CdpAgentkitWrapper
from models.strategy import (
    StrategyCreate,
    StrategyState,
    MorphoMarketInfo,
    LeverageMode
)

logger = logging.getLogger(__name__)

class MorphoService:
    """Service for interacting with Morpho protocol"""
    
    def __init__(self, cdp_wrapper: CdpAgentkitWrapper):
        self.cdp_wrapper = cdp_wrapper
        self.ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
        self.USDC_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        self.MORPHO_MARKETS = {
            "ETH-USDC": {
                "address": "0x...",  # Add actual market address
                "ltv": Decimal("0.825"),
                "liquidation_threshold": Decimal("0.85"),
                "base_currency": "ETH",
                "quote_currency": "USDC"
            }
        }
        
    async def get_market_info(self, market_id: str = "ETH-USDC") -> MorphoMarketInfo:
        """Get current market information"""
        try:
            market = self.MORPHO_MARKETS[market_id]
            result = await self.cdp_wrapper.execute_action(
                "get_market_info",
                {"market_address": market["address"]}
            )
            
            if not result.success:
                raise Exception(f"Failed to get market info: {result.error}")
                
            return MorphoMarketInfo(
                supply_apy=Decimal(str(result.data["supply_apy"])),
                borrow_apy=Decimal(str(result.data["borrow_apy"])),
                available_liquidity=Decimal(str(result.data["available_liquidity"])),
                total_supplied=Decimal(str(result.data["total_supplied"])),
                total_borrowed=Decimal(str(result.data["total_borrowed"])),
                utilization_rate=Decimal(str(result.data["utilization_rate"])),
                oracle_price=Decimal(str(result.data["oracle_price"])),
                updated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error getting market info: {str(e)}")
            raise
            
    async def execute_leverage_loop(
        self,
        strategy_id: str,
        initial_collateral: Decimal,
        target_leverage: Decimal,
        max_slippage: Decimal
    ) -> Dict[str, Any]:
        """Execute the leveraged looping strategy"""
        try:
            # 1. Initial deposit
            deposit_result = await self.cdp_wrapper.execute_action(
                "morpho_deposit",
                {
                    "token": self.ETH_ADDRESS,
                    "amount": str(initial_collateral),
                    "market": self.MORPHO_MARKETS["ETH-USDC"]["address"]
                }
            )
            
            if not deposit_result.success:
                raise Exception(f"Initial deposit failed: {deposit_result.error}")
                
            current_collateral = initial_collateral
            current_debt = Decimal("0")
            loops_executed = 0
            
            # 2. Execute leverage loops
            while current_debt / current_collateral < target_leverage and loops_executed < 10:
                # Calculate safe borrow amount
                max_borrow = (current_collateral * self.MORPHO_MARKETS["ETH-USDC"]["ltv"]) - current_debt
                borrow_amount = max_borrow * Decimal("0.95")  # 95% of max to be safe
                
                # Execute borrow
                borrow_result = await self.cdp_wrapper.execute_action(
                    "morpho_borrow",
                    {
                        "market": self.MORPHO_MARKETS["ETH-USDC"]["address"],
                        "amount": str(borrow_amount),
                        "max_slippage": str(max_slippage)
                    }
                )
                
                if not borrow_result.success:
                    break
                    
                current_debt += borrow_amount
                
                # Convert USDC to ETH and deposit
                swap_result = await self.cdp_wrapper.execute_action(
                    "swap",
                    {
                        "token_in": self.USDC_ADDRESS,
                        "token_out": self.ETH_ADDRESS,
                        "amount_in": str(borrow_amount),
                        "max_slippage": str(max_slippage)
                    }
                )
                
                if not swap_result.success:
                    break
                    
                eth_received = Decimal(str(swap_result.data["amount_out"]))
                current_collateral += eth_received
                
                # Deposit new ETH collateral
                await self.cdp_wrapper.execute_action(
                    "morpho_deposit",
                    {
                        "token": self.ETH_ADDRESS,
                        "amount": str(eth_received),
                        "market": self.MORPHO_MARKETS["ETH-USDC"]["address"]
                    }
                )
                
                loops_executed += 1
                
            return {
                "success": True,
                "loops_executed": loops_executed,
                "final_collateral": current_collateral,
                "final_debt": current_debt,
                "achieved_leverage": current_debt / current_collateral
            }
            
        except Exception as e:
            logger.error(f"Error executing leverage loop: {str(e)}")
            return {"success": False, "error": str(e)}
            
    async def get_position_state(self, strategy_id: str) -> StrategyState:
        """Get current state of a strategy position"""
        try:
            result = await self.cdp_wrapper.execute_action(
                "get_position",
                {"strategy_id": strategy_id}
            )
            
            if not result.success:
                raise Exception(f"Failed to get position: {result.error}")
                
            market_info = await self.get_market_info()
            
            return StrategyState(
                current_leverage=Decimal(str(result.data["leverage"])),
                current_ltv=Decimal(str(result.data["ltv"])),
                eth_collateral=Decimal(str(result.data["collateral"])),
                usdc_borrowed=Decimal(str(result.data["debt"])),
                total_value_eth=Decimal(str(result.data["total_value_eth"])),
                total_value_usd=Decimal(str(result.data["total_value_usd"])),
                health_factor=Decimal(str(result.data["health_factor"])),
                estimated_apy=self._calculate_estimated_apy(
                    result.data,
                    market_info
                ),
                next_rebalance=datetime.utcnow() + timedelta(hours=1),
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error getting position state: {str(e)}")
            raise
            
    async def emergency_exit(self, strategy_id: str) -> bool:
        """Execute emergency exit using flash loans"""
        try:
            # Get current position
            position = await self.get_position_state(strategy_id)
            
            # Calculate flash loan amount needed
            flash_loan_amount = position.usdc_borrowed
            
            # Execute flash loan repayment
            result = await self.cdp_wrapper.execute_action(
                "flash_loan_repayment",
                {
                    "strategy_id": strategy_id,
                    "amount": str(flash_loan_amount),
                    "withdraw_collateral": True
                }
            )
            
            return result.success
            
        except Exception as e:
            logger.error(f"Error executing emergency exit: {str(e)}")
            return False
            
    def _calculate_estimated_apy(
        self,
        position_data: Dict[str, Any],
        market_info: MorphoMarketInfo
    ) -> Decimal:
        """Calculate estimated APY based on current position"""
        try:
            leverage = Decimal(str(position_data["leverage"]))
            supply_apy = market_info.supply_apy
            borrow_apy = market_info.borrow_apy
            
            # Base yield from supply
            base_yield = supply_apy
            
            # Cost from borrowing
            borrowing_cost = borrow_apy * (leverage - 1)
            
            # Net APY
            net_apy = (base_yield * leverage) - borrowing_cost
            
            return net_apy
            
        except Exception as e:
            logger.error(f"Error calculating APY: {str(e)}")
            return Decimal("0") 
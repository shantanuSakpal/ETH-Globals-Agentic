from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal

MORPHO_REPAY_PROMPT = """
Repay borrowed assets on Morpho protocol.
Requires position ID, repay amount, and withdrawal preferences.
"""

class MorphoRepayInput(BaseModel):
    """Input parameters for repayment"""
    position_id: str = Field(
        ...,
        description="Unique identifier of the position"
    )
    repay_amount: Decimal = Field(
        ...,
        gt=0,
        description="Amount to repay"
    )
    withdraw_collateral: bool = Field(
        default=False,
        description="Whether to withdraw remaining collateral after repayment"
    )
    max_slippage: Optional[Decimal] = Field(
        default=0.005,
        ge=0,
        le=0.1,
        description="Maximum allowed slippage (0.5% default)"
    )

async def morpho_repay(
    position_id: str,
    repay_amount: Decimal,
    withdraw_collateral: bool = False,
    max_slippage: Optional[Decimal] = None
) -> dict:
    """
    Execute repay action on Morpho protocol
    
    Args:
        position_id: Position identifier
        repay_amount: Amount to repay
        withdraw_collateral: Whether to withdraw remaining collateral
        max_slippage: Maximum allowed slippage
        
    Returns:
        dict: Result of repay action
    """
    try:
        # Implement repay logic using CDP AgentKit
        return {
            "success": True,
            "position_id": position_id,
            "repaid_amount": repay_amount,
            "collateral_withdrawn": withdraw_collateral
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

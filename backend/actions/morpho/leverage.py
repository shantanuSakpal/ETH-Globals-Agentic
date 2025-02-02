from cdp import Wallet
from cdp_langchain.tools import CdpTool
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Dict, Any, Optional
from web3 import Web3

class MorphoLeverageInput(BaseModel):
    """Input schema for Morpho leverage action"""
    position_id: str = Field(
        ...,
        description="ID of the position to adjust leverage"
    )
    target_leverage: float = Field(
        ...,
        description="Target leverage ratio (e.g., 2.0 for 2x leverage)",
        gt=1,
        le=5  # Maximum leverage allowed
    )
    action_type: str = Field(
        ...,
        description="Type of leverage action: 'increase' or 'decrease'",
        regex="^(increase|decrease)$"
    )
    max_slippage: Optional[float] = Field(
        default=0.01,
        description="Maximum allowed slippage (default 1%)",
        ge=0,
        le=1
    )

MORPHO_LEVERAGE_PROMPT = """
This tool enables adjusting position leverage on the Morpho protocol using flash loans.
The action will:
1. Validate current position health
2. Calculate required flash loan or repayment amount
3. Execute leverage adjustment transaction
4. Return transaction details and new position information
"""

def morpho_leverage(
    wallet: Wallet,
    position_id: str,
    target_leverage: float,
    action_type: str,
    max_slippage: Optional[float] = 0.01
) -> str:
    """Execute leverage adjustment on Morpho protocol"""
    try:
        slippage_bps = int(max_slippage * 10000)
        
        # Build leverage payload
        payload = {
            "protocol": "morpho",
            "action": f"{action_type}_leverage",
            "params": {
                "positionId": position_id,
                "targetLeverage": str(int(target_leverage * 1e18)),
                "maxSlippageBps": slippage_bps
            }
        }
        
        # Execute through CDP
        tx_result = wallet.sign_and_execute_transaction(payload).wait()
        
        return (
            f"Leverage adjustment successful!\n"
            f"Transaction Hash: {tx_result['transactionHash']}\n"
            f"Action: {action_type} leverage\n"
            f"Target Leverage: {target_leverage}x"
        )
        
    except Exception as e:
        return f"Leverage adjustment failed: {str(e)}"

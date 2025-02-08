from cdp import Wallet
from cdp_langchain.tools import CdpTool
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Dict, Any, Optional
from web3 import Web3

MORPHO_LEVERAGE_PROMPT = """
Adjust leverage for a Morpho protocol position.
Requires position ID, target leverage, and action type (increase/decrease).
"""

class MorphoLeverageInput(BaseModel):
    """Input parameters for leverage adjustment"""
    position_id: str = Field(
        ...,
        description="Unique identifier of the position"
    )
    target_leverage: Decimal = Field(
        ...,
        ge=1.0,
        description="Target leverage ratio"
    )
    action_type: str = Field(
        ...,
        pattern="^(increase|decrease)$",
        description="Type of leverage adjustment (increase/decrease)"
    )
    max_slippage: Optional[Decimal] = Field(
        default=0.005,
        ge=0,
        le=0.1,
        description="Maximum allowed slippage (0.5% default)"
    )

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

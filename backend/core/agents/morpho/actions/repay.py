from cdp import Wallet
from cdp_langchain.tools import CdpTool
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Dict, Any, Optional
from web3 import Web3

class MorphoRepayInput(BaseModel):
    """Input schema for Morpho repay action"""
    position_id: str = Field(
        ...,
        description="ID of the position to repay"
    )
    repay_amount: float = Field(
        ...,
        description="Amount to repay in token decimals",
        gt=0
    )
    withdraw_collateral: Optional[bool] = Field(
        default=False,
        description="Whether to withdraw remaining collateral after repayment"
    )
    max_slippage: Optional[float] = Field(
        default=0.01,
        description="Maximum allowed slippage (default 1%)"
    )

MORPHO_REPAY_PROMPT = """
This tool enables repaying borrowed assets on the Morpho protocol.
The action will:
1. Validate repayment parameters
2. Execute repayment transaction
3. Optionally withdraw remaining collateral
4. Return transaction details and updated position information
"""

def morpho_repay(
    wallet: Wallet,
    position_id: str,
    repay_amount: float,
    withdraw_collateral: bool = False,
    max_slippage: Optional[float] = 0.01
) -> str:
    """Execute repayment on Morpho protocol"""
    try:
        amount_in_wei = Web3.to_wei(repay_amount, 'ether')
        slippage_bps = int(max_slippage * 10000)
        
        # Build repay payload
        payload = {
            "protocol": "morpho",
            "action": "repay",
            "params": {
                "positionId": position_id,
                "amount": str(amount_in_wei),
                "withdrawCollateral": withdraw_collateral,
                "maxSlippageBps": slippage_bps
            }
        }
        
        # Execute through CDP
        tx_result = wallet.sign_and_execute_transaction(payload).wait()
        
        return (
            f"Repay transaction successful!\n"
            f"Transaction Hash: {tx_result['transactionHash']}\n"
            f"Repaid Amount: {repay_amount}"
        )
        
    except Exception as e:
        return f"Repay action failed: {str(e)}"

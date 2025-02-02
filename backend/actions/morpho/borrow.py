from cdp import Wallet
from cdp_langchain.tools import CdpTool
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Dict, Any, Optional
from web3 import Web3

# Define Borrow Action Input Schema
class MorphoBorrowInput(BaseModel):
    """Input argument schema for Morpho borrow action."""
    
    collateral_token: str = Field(
        ...,
        description="Address of the collateral token"
    )
    debt_token: str = Field(
        ...,
        description="Address of the token to borrow"
    )
    borrow_amount: float = Field(
        ...,
        description="Amount to borrow in token decimals",
        gt=0
    )
    max_slippage: Optional[float] = Field(
        default=0.01,
        description="Maximum allowed slippage (default 1%)",
        ge=0,
        le=1
    )

MORPHO_BORROW_PROMPT = """
This tool enables borrowing assets from the Morpho protocol using provided collateral.
The action will:
1. Validate the borrowing parameters
2. Check position health
3. Execute the borrow transaction
4. Return transaction details and new position information
"""

def morpho_borrow(
    wallet: Wallet,
    collateral_token: str,
    debt_token: str,
    borrow_amount: float,
    max_slippage: Optional[float] = 0.01
) -> str:
    """Execute a borrow action on Morpho protocol.
    
    Args:
        wallet: CDP Wallet instance
        collateral_token: Collateral token address
        debt_token: Token to borrow address
        borrow_amount: Amount to borrow
        max_slippage: Maximum allowed slippage
        
    Returns:
        str: Transaction result details
    """
    try:
        # Convert amount to Wei
        amount_in_wei = Web3.to_wei(borrow_amount, 'ether')
        slippage_bps = int(max_slippage * 10000)
        
        # Build borrow payload
        payload = {
            "protocol": "morpho",
            "action": "borrow",
            "params": {
                "collateralToken": collateral_token,
                "debtToken": debt_token,
                "amount": str(amount_in_wei),
                "maxSlippageBps": slippage_bps
            }
        }
        
        # Sign and execute transaction through CDP
        tx_result = wallet.sign_and_execute_transaction(payload).wait()
        
        # Format response
        return (
            f"Borrow transaction successful!\n"
            f"Transaction Hash: {tx_result['transactionHash']}\n"
            f"Borrowed Amount: {borrow_amount} {debt_token}\n"
            f"Collateral Token: {collateral_token}"
        )
        
    except Exception as e:
        return f"Borrow action failed: {str(e)}"

def initialize_morpho_tools(agentkit: CdpAgentkitWrapper, tools: list) -> list:
    """Initialize Morpho-specific CDP tools"""
    
    # Create borrow tool
    borrow_tool = CdpTool(
        name="morpho_borrow",
        description=MORPHO_BORROW_PROMPT,
        cdp_agentkit_wrapper=agentkit,
        args_schema=MorphoBorrowInput,
        func=morpho_borrow
    )
    
    # Add to existing tools
    tools.append(borrow_tool)
    
    return tools

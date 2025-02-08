from cdp import Wallet
from cdp_langchain.tools import CdpTool
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Dict, Any, Optional
from web3 import Web3
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper

# Define Borrow Action Input Schema
class MorphoBorrowInput(BaseModel):
    """Input parameters for borrowing"""
    collateral_token: str = Field(
        ...,
        description="Address of collateral token"
    )
    debt_token: str = Field(
        ...,
        description="Address of token to borrow"
    )
    borrow_amount: Decimal = Field(
        ...,
        gt=0,
        description="Amount to borrow"
    )
    max_slippage: Optional[Decimal] = Field(
        default=0.005,
        ge=0,
        le=0.1,
        description="Maximum allowed slippage (0.5% default)"
    )

MORPHO_BORROW_PROMPT = """
Borrow assets from Morpho protocol using provided collateral.
Requires collateral token, debt token, and borrow amount.
"""

def morpho_borrow(
    wallet: Wallet,
    collateral_token: str,
    debt_token: str,
    borrow_amount: Decimal,
    max_slippage: Optional[Decimal] = None
) -> dict:
    """
    Execute borrow action on Morpho protocol
    
    Args:
        wallet: CDP Wallet instance
        collateral_token: Address of collateral token
        debt_token: Address of token to borrow
        borrow_amount: Amount to borrow
        max_slippage: Maximum allowed slippage
        
    Returns:
        dict: Result of borrow action
    """
    try:
        # Convert amount to Wei
        amount_in_wei = Web3.to_wei(float(borrow_amount), 'ether')
        slippage_bps = int(max_slippage * 10000) if max_slippage else 500
        
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
        return {
            "success": True,
            "transaction_hash": tx_result['transactionHash'],
            "borrowed_amount": borrow_amount,
            "collateral_token": collateral_token,
            "debt_token": debt_token
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

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

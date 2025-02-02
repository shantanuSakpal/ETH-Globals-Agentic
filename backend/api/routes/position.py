from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from models.position import (
    PositionCreate,
    PositionUpdate,
    PositionResponse,
    PositionList
)
from services.morpho_client import MorphoClient
from config.settings import get_settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize Morpho client
morpho_client = MorphoClient(
    web3_provider=settings.WEB3_PROVIDER_URI,
    contract_address=settings.MORPHO_CONTRACT_ADDRESS
)

@router.post("/", response_model=PositionResponse)
async def open_position(position: PositionCreate):
    """
    Open a new trading position
    
    Args:
        position: Position creation parameters
    """
    try:
        # Validate strategy exists
        if not await _validate_strategy(position.strategy_id):
            raise HTTPException(
                status_code=404,
                detail=f"Strategy {position.strategy_id} not found"
            )
            
        # Open position
        success = await morpho_client.open_position(
            size=position.size,
            leverage=position.leverage,
            position_type=position.position_type
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to open position"
            )
            
        # Get position details
        position_data = await morpho_client.get_position(
            position.strategy_id
        )
        
        return position_data
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error opening position: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error opening position: {str(e)}"
        )

@router.get("/{position_id}", response_model=PositionResponse)
async def get_position(position_id: str):
    """
    Get details of a specific position
    
    Args:
        position_id: ID of the position
    """
    try:
        position = await morpho_client.get_position(position_id)
        if not position:
            raise HTTPException(
                status_code=404,
                detail=f"Position {position_id} not found"
            )
        return position
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching position {position_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching position: {str(e)}"
        )

@router.get("/strategy/{strategy_id}", response_model=PositionList)
async def get_strategy_positions(strategy_id: str):
    """
    Get all positions for a strategy
    
    Args:
        strategy_id: ID of the strategy
    """
    try:
        # Validate strategy exists
        if not await _validate_strategy(strategy_id):
            raise HTTPException(
                status_code=404,
                detail=f"Strategy {strategy_id} not found"
            )
            
        # Get positions
        positions = await _get_strategy_positions(strategy_id)
        return {"positions": positions}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching positions for strategy {strategy_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching positions: {str(e)}"
        )

@router.put("/{position_id}", response_model=PositionResponse)
async def update_position(
    position_id: str,
    position_update: PositionUpdate
):
    """
    Update an existing position
    
    Args:
        position_id: ID of the position to update
        position_update: Position update parameters
    """
    try:
        # Get current position
        current_position = await morpho_client.get_position(position_id)
        if not current_position:
            raise HTTPException(
                status_code=404,
                detail=f"Position {position_id} not found"
            )
            
        # Calculate size delta
        if position_update.size is not None:
            size_delta = position_update.size - current_position["size"]
            
            # Adjust position
            success = await morpho_client.adjust_position(
                position_id=position_id,
                size_delta=size_delta
            )
            
            if not success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to update position"
                )
                
        # Update stop loss and take profit
        if position_update.stop_loss is not None:
            current_position["stop_loss"] = position_update.stop_loss
            
        if position_update.take_profit is not None:
            current_position["take_profit"] = position_update.take_profit
            
        return current_position
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating position {position_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating position: {str(e)}"
        )

@router.delete("/{position_id}")
async def close_position(position_id: str):
    """
    Close an existing position
    
    Args:
        position_id: ID of the position to close
    """
    try:
        # Validate position exists
        position = await morpho_client.get_position(position_id)
        if not position:
            raise HTTPException(
                status_code=404,
                detail=f"Position {position_id} not found"
            )
            
        # Close position
        success = await morpho_client.close_position(position_id)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to close position"
            )
            
        return {
            "status": "success",
            "message": f"Position {position_id} closed successfully"
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error closing position {position_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error closing position: {str(e)}"
        )

async def _validate_strategy(strategy_id: str) -> bool:
    """Validate that a strategy exists"""
    # Implement strategy validation logic
    return True

async def _get_strategy_positions(strategy_id: str) -> List[dict]:
    """Get all positions for a strategy"""
    # Implement position fetching logic
    return [] 
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from models.position import (
    PositionCreate,
    PositionUpdate,
    PositionResponse,
    PositionList
)
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper
from config.settings import get_settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize CDP AgentKit
cdp_wrapper = None
cdp_toolkit = None

def get_cdp_wrapper():
    global cdp_wrapper
    if cdp_wrapper is None:
        try:
            cdp_wrapper = CdpAgentkitWrapper(
                api_key_name=settings.CDP_API_KEY_NAME,
                api_key_private_key=settings.CDP_API_KEY_PRIVATE_KEY,
                network_id=settings.NETWORK_ID
            )
            logger.info("CDP wrapper initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize CDP wrapper: {str(e)}")
            if not settings.DEBUG:
                raise
    return cdp_wrapper

def get_cdp_toolkit():
    global cdp_toolkit
    if cdp_toolkit is None:
        wrapper = get_cdp_wrapper()
        if wrapper:
            try:
                cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(wrapper)
                logger.info("CDP toolkit initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize CDP toolkit: {str(e)}")
                if not settings.DEBUG:
                    raise
    return cdp_toolkit

@router.post("/", response_model=PositionResponse)
async def open_position(position: PositionCreate):
    """
    Open a new trading position using CDP AgentKit
    
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
            
        # Open position using CDP AgentKit
        result = await get_cdp_toolkit().execute_action(
            "open_position",
            {
                "size": position.size,
                "leverage": position.leverage,
                "position_type": position.position_type,
                "strategy_id": position.strategy_id
            }
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to open position: {result.error}"
            )
            
        return result.data
        
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
        result = await get_cdp_toolkit().execute_action(
            "get_position",
            {"position_id": position_id}
        )
        
        if not result.success:
            raise HTTPException(
                status_code=404,
                detail=f"Position {position_id} not found"
            )
            
        return result.data
        
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
            
        result = await get_cdp_toolkit().execute_action(
            "get_strategy_positions",
            {"strategy_id": strategy_id}
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch positions: {result.error}"
            )
            
        return {"positions": result.data}
        
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
        result = await get_cdp_toolkit().execute_action(
            "update_position",
            {
                "position_id": position_id,
                **position_update.model_dump(exclude_unset=True)
            }
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update position: {result.error}"
            )
            
        return result.data
        
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
        result = await get_cdp_toolkit().execute_action(
            "close_position",
            {"position_id": position_id}
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to close position: {result.error}"
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
    try:
        result = await get_cdp_toolkit().execute_action(
            "validate_strategy",
            {"strategy_id": strategy_id}
        )
        return result.success
    except Exception:
        return False 
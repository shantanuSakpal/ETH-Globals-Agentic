from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.api import (
    StrategyCreate,
    StrategyUpdate,
    StrategyResponse,
    StrategyList
)
from backend.agents.morpho.agent import MorphoAgent
from config.settings import get_settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

@router.get("/", response_model=StrategyList)
async def list_strategies():
    """List all available strategies"""
    try:
        # In a real implementation, this would fetch from a database
        strategies = [
            {
                "id": "eth-usdc-loop",
                "name": "ETH-USDC Loop Strategy",
                "description": "Leveraged ETH-USDC loop strategy using Morpho protocol",
                "status": "active",
                "risk_level": "medium"
            }
        ]
        return {"strategies": strategies}
    except Exception as e:
        logger.error(f"Error listing strategies: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=StrategyResponse)
async def create_strategy(strategy: StrategyCreate):
    """Create a new strategy instance"""
    try:
        # Initialize the Morpho agent with the strategy parameters
        agent = MorphoAgent(
            strategy_params=strategy.dict(),
            settings=settings
        )
        
        # In a real implementation, save to database and return the created strategy
        return {
            "id": "new-strategy-id",
            "status": "created",
            **strategy.dict()
        }
    except Exception as e:
        logger.error(f"Error creating strategy: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(strategy_id: str):
    """Get details of a specific strategy"""
    try:
        # In a real implementation, fetch from database
        if strategy_id != "eth-usdc-loop":
            raise HTTPException(status_code=404, detail="Strategy not found")
            
        return {
            "id": strategy_id,
            "name": "ETH-USDC Loop Strategy",
            "description": "Leveraged ETH-USDC loop strategy using Morpho protocol",
            "status": "active",
            "risk_level": "medium"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching strategy {strategy_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(strategy_id: str, strategy: StrategyUpdate):
    """Update an existing strategy"""
    try:
        # In a real implementation, update in database
        if strategy_id != "eth-usdc-loop":
            raise HTTPException(status_code=404, detail="Strategy not found")
            
        return {
            "id": strategy_id,
            **strategy.dict()
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating strategy {strategy_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{strategy_id}")
async def delete_strategy(strategy_id: str):
    """Delete a strategy"""
    try:
        # In a real implementation, delete from database
        if strategy_id != "eth-usdc-loop":
            raise HTTPException(status_code=404, detail="Strategy not found")
            
        return {"status": "success", "message": f"Strategy {strategy_id} deleted"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting strategy {strategy_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 
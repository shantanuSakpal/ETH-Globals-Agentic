from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def calculate_metrics(
    prices: List[float],
    timestamps: List[datetime],
    window: int = 24
) -> Dict[str, float]:
    """
    Calculate various trading metrics from price data
    
    Args:
        prices: List of prices
        timestamps: List of corresponding timestamps
        window: Window size for calculations in hours
        
    Returns:
        Dict containing calculated metrics
    """
    try:
        prices_array = np.array(prices)
        returns = np.diff(prices_array) / prices_array[:-1]
        
        # Calculate metrics
        volatility = np.std(returns) * np.sqrt(365 * 24)  # Annualized
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(365 * 24)
        max_drawdown = calculate_max_drawdown(prices_array)
        
        return {
            "volatility": float(volatility),
            "sharpe_ratio": float(sharpe_ratio),
            "max_drawdown": float(max_drawdown),
            "current_price": float(prices[-1]),
            "price_change_24h": calculate_price_change(prices, window)
        }
        
    except Exception as e:
        logger.error(f"Error calculating metrics: {str(e)}")
        return {
            "volatility": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "current_price": 0.0,
            "price_change_24h": 0.0
        }

def calculate_position_metrics(
    position: Dict[str, Any],
    current_price: float
) -> Dict[str, float]:
    """
    Calculate position-specific metrics
    
    Args:
        position: Position data
        current_price: Current asset price
        
    Returns:
        Dict containing position metrics
    """
    try:
        entry_price = position["entry_price"]
        size = position["size"]
        leverage = position["leverage"]
        
        # Calculate PnL
        price_change = (current_price - entry_price) / entry_price
        pnl = size * price_change * leverage
        pnl_percentage = price_change * leverage * 100
        
        # Calculate liquidation price
        liq_threshold = 1 / leverage
        liquidation_price = entry_price * (1 - liq_threshold)
        
        return {
            "pnl": float(pnl),
            "pnl_percentage": float(pnl_percentage),
            "liquidation_price": float(liquidation_price),
            "margin_ratio": calculate_margin_ratio(
                current_price,
                entry_price,
                leverage
            )
        }
        
    except Exception as e:
        logger.error(f"Error calculating position metrics: {str(e)}")
        return {
            "pnl": 0.0,
            "pnl_percentage": 0.0,
            "liquidation_price": 0.0,
            "margin_ratio": 0.0
        }

def calculate_optimal_leverage(
    volatility: float,
    target_risk: float = 0.1
) -> float:
    """
    Calculate optimal leverage based on volatility
    
    Args:
        volatility: Asset volatility
        target_risk: Target risk level
        
    Returns:
        float: Optimal leverage
    """
    try:
        # Kelly criterion-based calculation
        return min(1 / volatility, target_risk / volatility)
        
    except Exception as e:
        logger.error(f"Error calculating optimal leverage: {str(e)}")
        return 1.0

def calculate_max_drawdown(prices: np.ndarray) -> float:
    """
    Calculate maximum drawdown from price series
    
    Args:
        prices: Array of prices
        
    Returns:
        float: Maximum drawdown as a percentage
    """
    try:
        peak = prices[0]
        max_dd = 0
        
        for price in prices[1:]:
            if price > peak:
                peak = price
            dd = (peak - price) / peak
            max_dd = max(max_dd, dd)
            
        return max_dd * 100
        
    except Exception as e:
        logger.error(f"Error calculating max drawdown: {str(e)}")
        return 0.0

def calculate_margin_ratio(
    current_price: float,
    entry_price: float,
    leverage: float
) -> float:
    """
    Calculate current margin ratio
    
    Args:
        current_price: Current asset price
        entry_price: Position entry price
        leverage: Position leverage
        
    Returns:
        float: Current margin ratio
    """
    try:
        price_change = (current_price - entry_price) / entry_price
        return (1 / leverage) + price_change
        
    except Exception as e:
        logger.error(f"Error calculating margin ratio: {str(e)}")
        return 0.0

def calculate_price_change(
    prices: List[float],
    window: int = 24
) -> float:
    """
    Calculate price change over a time window
    
    Args:
        prices: List of prices
        window: Time window in hours
        
    Returns:
        float: Price change as a percentage
    """
    try:
        if len(prices) < window:
            return 0.0
            
        start_price = prices[-window]
        end_price = prices[-1]
        return ((end_price - start_price) / start_price) * 100
        
    except Exception as e:
        logger.error(f"Error calculating price change: {str(e)}")
        return 0.0

def validate_strategy_params(params: Dict[str, Any]) -> bool:
    """
    Validate strategy parameters
    
    Args:
        params: Strategy parameters
        
    Returns:
        bool: True if parameters are valid
    """
    try:
        required_params = [
            "max_leverage",
            "min_collateral_ratio",
            "target_apy",
            "rebalance_threshold",
            "position_size"
        ]
        
        # Check required parameters
        for param in required_params:
            if param not in params:
                logger.error(f"Missing required parameter: {param}")
                return False
                
        # Validate parameter values
        if params["max_leverage"] < 1:
            logger.error("max_leverage must be >= 1")
            return False
            
        if params["min_collateral_ratio"] < 1:
            logger.error("min_collateral_ratio must be >= 1")
            return False
            
        if params["target_apy"] < 0:
            logger.error("target_apy must be >= 0")
            return False
            
        if params["rebalance_threshold"] < 0:
            logger.error("rebalance_threshold must be >= 0")
            return False
            
        if params["position_size"] < 0:
            logger.error("position_size must be >= 0")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error validating strategy parameters: {str(e)}")
        return False

def format_position_data(
    position: Dict[str, Any],
    metrics: Dict[str, float]
) -> Dict[str, Any]:
    """
    Format position data for API response
    
    Args:
        position: Position data
        metrics: Position metrics
        
    Returns:
        Dict containing formatted position data
    """
    try:
        return {
            "id": position.get("id", ""),
            "type": position.get("type", ""),
            "size": position.get("size", 0.0),
            "leverage": position.get("leverage", 1.0),
            "entry_price": position.get("entry_price", 0.0),
            "liquidation_price": metrics.get("liquidation_price", 0.0),
            "margin_ratio": metrics.get("margin_ratio", 0.0),
            "pnl": metrics.get("pnl", 0.0),
            "pnl_percentage": metrics.get("pnl_percentage", 0.0),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error formatting position data: {str(e)}")
        return {}
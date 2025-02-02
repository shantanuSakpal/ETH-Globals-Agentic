from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from models.market import MarketData, MarketDataList
from services.price_feed import PriceFeed
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
price_feed = PriceFeed()

@router.get("/price/{symbol}", response_model=MarketData)
async def get_current_price(symbol: str):
    """
    Get current price for a trading pair
    
    Args:
        symbol: Trading pair symbol (e.g., 'ETH-USD')
    """
    try:
        market_data = await price_feed.get_market_data(symbol)
        return market_data
        
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching price data: {str(e)}"
        )

@router.get("/markets", response_model=MarketDataList)
async def get_markets_data(
    symbols: Optional[List[str]] = Query(None),
    include_metadata: bool = False
):
    """
    Get market data for multiple trading pairs
    
    Args:
        symbols: List of trading pair symbols
        include_metadata: Whether to include additional market metadata
    """
    try:
        if symbols is None:
            symbols = ["ETH-USD", "BTC-USD", "USDC-USD"]  # Default markets
            
        markets_data = []
        for symbol in symbols:
            try:
                market_data = await price_feed.get_market_data(symbol)
                if include_metadata:
                    market_data = await _enrich_market_data(market_data)
                markets_data.append(market_data)
            except Exception as e:
                logger.warning(f"Error fetching data for {symbol}: {str(e)}")
                continue
                
        return {"markets": markets_data}
        
    except Exception as e:
        logger.error(f"Error fetching markets data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching markets data: {str(e)}"
        )

@router.get("/historical/{symbol}")
async def get_historical_data(
    symbol: str,
    interval: str = Query("1h", regex="^[1-9][0-9]*(m|h|d)$"),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    """
    Get historical price data
    
    Args:
        symbol: Trading pair symbol
        interval: Time interval (e.g., '1h', '1d')
        start_time: Start time for historical data
        end_time: End time for historical data
    """
    try:
        # Set default time range if not provided
        if end_time is None:
            end_time = datetime.utcnow()
        if start_time is None:
            start_time = end_time - timedelta(days=7)
            
        historical_data = await price_feed.get_historical_data(
            symbol,
            start_time,
            end_time,
            interval
        )
        
        return {
            "symbol": symbol,
            "interval": interval,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "data": historical_data
        }
        
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching historical data: {str(e)}"
        )

@router.get("/aggregated/{symbol}")
async def get_aggregated_price(
    symbol: str,
    sources: Optional[List[str]] = Query(None)
):
    """
    Get price aggregated from multiple sources
    
    Args:
        symbol: Trading pair symbol
        sources: List of price sources to use
    """
    try:
        aggregated_price = await price_feed.get_aggregated_price(
            symbol,
            sources
        )
        
        return {
            "symbol": symbol,
            "price": aggregated_price,
            "sources": sources,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching aggregated price for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching aggregated price: {str(e)}"
        )

async def _enrich_market_data(market_data: dict) -> dict:
    """Add additional market metadata"""
    try:
        # Add market specific metadata
        market_data.update({
            "market_cap": 0.0,  # Add actual market cap
            "total_supply": 0.0,  # Add actual supply
            "circulating_supply": 0.0,  # Add actual circulating supply
            "trading_pairs": [],  # Add available trading pairs
            "exchanges": []  # Add exchanges where traded
        })
        return market_data
        
    except Exception as e:
        logger.error(f"Error enriching market data: {str(e)}")
        return market_data
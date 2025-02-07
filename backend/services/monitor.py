from typing import Dict, Any
import asyncio
import logging
from models.websocket import WSMessage, WSMessageType
from services.price_feed import PriceFeed
from datetime import datetime

logger = logging.getLogger(__name__)

class StrategyMonitor:
    def __init__(self, manager, price_feed: PriceFeed):
        self.manager = manager
        self.price_feed = price_feed
        self._monitors: Dict[str, asyncio.Task] = {}
        self.logger = logging.getLogger(__name__)
        
    async def start_monitoring(self, vault_id: str):
        """Start monitoring a strategy vault"""
        if vault_id in self._monitors:
            return
            
        self._monitors[vault_id] = asyncio.create_task(
            self._monitor_loop(vault_id)
        )
        
    async def _monitor_loop(self, vault_id: str):
        """Main monitoring loop for strategy metrics"""
        #while True:
        retry_count = 0
        while retry_count < 3:
            try:
                # Get strategy metrics
                metrics = await self._get_strategy_metrics(vault_id)
                
                # Create WebSocket message
                message = WSMessage(
                    type=WSMessageType.MONITOR_UPDATE,
                    data={
                        "vault_id": vault_id,
                        "metrics": metrics,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                # Broadcast to subscribed clients
                await self.manager.broadcast_message(
                    message=message,
                    topic=f"strategy_{vault_id}"
                )
                
                retry_count = 0  # Reset on success
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                #   logger.error(f"Monitor error for {vault_id}: {str(e)}")
                # break
                retry_count += 1
                logger.error(f"Monitor error (attempt {retry_count}): {str(e)}")
                await asyncio.sleep(5 * retry_count)  # Exponential backoff
                
    async def _get_strategy_metrics(self, vault_id: str) -> Dict[str, Any]:
        """Get current metrics for a strategy"""
        # Implement metric collection logic here
        return {
            "pnl": 0.0,
            "current_value": 0.0,
            "risk_level": "medium",
            "market_data": await self.price_feed.get_market_data("ETH-USD")
        }

    async def notify_risk_level_change(self, vault_id: str, risk_level: str):
        """Notify clients about risk level changes"""
        message = WSMessage(
            type=WSMessageType.MONITOR_UPDATE,
            data={
                "vault_id": vault_id,
                "risk_level": risk_level,
                "alert": "Risk level has changed",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        await self.manager.broadcast_message(
            message=message,
            topic=f"strategy_{vault_id}"
        )

    async def stop_monitoring(self, vault_id: str):
        """Stop monitoring a strategy vault"""
        if task := self._monitors.pop(vault_id, None):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from config.settings import Settings

class BaseAgent(ABC):
    """
    Base class for all trading agents.
    Implements common functionality and defines interface that all agents must implement.
    """
    
    def __init__(self, strategy_params: Dict[str, Any], settings: Settings):
        """
        Initialize the base agent with strategy parameters and settings.
        
        Args:
            strategy_params: Dictionary containing strategy-specific parameters
            settings: Application settings
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.strategy_params = strategy_params
        self.settings = settings
        self.is_running = False
        self.current_position = None
        self.performance_metrics = {}
        
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the agent with necessary setup.
        Should be implemented by concrete classes.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def analyze_market(self) -> Dict[str, Any]:
        """
        Analyze current market conditions and return analysis results.
        Should be implemented by concrete classes.
        
        Returns:
            Dict containing market analysis results
        """
        pass
    
    @abstractmethod
    async def make_decision(self) -> Dict[str, Any]:
        """
        Make trading decisions based on market analysis.
        Should be implemented by concrete classes.
        
        Returns:
            Dict containing trading decisions
        """
        pass
    
    @abstractmethod
    async def execute_trade(self, decision: Dict[str, Any]) -> bool:
        """
        Execute trading decision.
        Should be implemented by concrete classes.
        
        Args:
            decision: Dictionary containing trading decision parameters
            
        Returns:
            bool: True if trade was executed successfully, False otherwise
        """
        pass
    
    async def start(self) -> bool:
        """
        Start the trading agent.
        
        Returns:
            bool: True if agent was started successfully, False otherwise
        """
        try:
            self.logger.info("Starting agent...")
            if not await self.initialize():
                self.logger.error("Failed to initialize agent")
                return False
                
            self.is_running = True
            self.logger.info("Agent started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting agent: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """
        Stop the trading agent.
        
        Returns:
            bool: True if agent was stopped successfully, False otherwise
        """
        try:
            self.logger.info("Stopping agent...")
            self.is_running = False
            # Implement cleanup logic here
            self.logger.info("Agent stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping agent: {str(e)}")
            return False
    
    async def update_performance_metrics(self) -> None:
        """
        Update agent's performance metrics.
        """
        try:
            # Implement performance metric calculation logic here
            self.performance_metrics.update({
                "pnl": 0.0,  # Calculate actual PnL
                "roi": 0.0,  # Calculate actual ROI
                "sharpe_ratio": 0.0,  # Calculate Sharpe ratio
                "max_drawdown": 0.0,  # Calculate max drawdown
            })
        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the agent.
        
        Returns:
            Dict containing agent's current status and metrics
        """
        return {
            "is_running": self.is_running,
            "current_position": self.current_position,
            "performance_metrics": self.performance_metrics,
            "strategy_params": self.strategy_params
        }
    
    @abstractmethod
    async def handle_error(self, error: Exception) -> None:
        """
        Handle errors that occur during agent operation.
        Should be implemented by concrete classes.
        
        Args:
            error: The exception that occurred
        """
        pass

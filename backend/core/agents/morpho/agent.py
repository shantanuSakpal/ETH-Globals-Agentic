from datetime import datetime
from typing import Dict, Any, Optional, Set, List
from decimal import Decimal

from cdp import Wallet
from config.settings import get_settings
from core.agents.morpho.actions.repay import MORPHO_REPAY_PROMPT, morpho_repay
from fastapi import WebSocket
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper
from core.agents.base_agent import BaseAgent
from services.price_feed import PriceFeed
from enum import Enum
import logging
import asyncio
from langchain.schema import HumanMessage
from cdp_langchain.tools import CdpTool
from core.agents.morpho.actions.borrow import MorphoBorrowInput, morpho_borrow, MORPHO_BORROW_PROMPT
from core.agents.morpho.actions.leverage import MORPHO_LEVERAGE_PROMPT, MorphoLeverageInput, morpho_leverage
from core.agents.morpho.actions.repay import MorphoRepayInput, morpho_repay
from cdp_agentkit_core.actions.morpho.deposit import MorphoDepositInput, deposit_to_morpho
from cdp_agentkit_core.actions.morpho.withdraw import MorphoWithdrawInput, withdraw_from_morpho

# Agent components
from core.agents.morpho.components.data_collector import DataCollector
from core.agents.morpho.components.decision_maker import DecisionMaker
from core.agents.morpho.components.emergency_handler import EmergencyHandler
from core.agents.morpho.components.performance_monitor import PerformanceMonitor
from core.agents.morpho.components.position_manager import PositionManager
from core.agents.morpho.components.risk_manager import RiskManager
from core.agents.morpho.components.strategy_analyzer import StrategyAnalyzer

class MessageType(Enum):
    STRATEGY_SELECT = "strategy_select"
    MARKET_UPDATE = "market_update"
    POSITION_UPDATE = "position_update"
    ERROR = "error"
    ACTION_RESULT = "action_result"

class MorphoAgent(BaseAgent):
    """
    Morpho Leveraged ETH Strategy Agent
    
    Strategy Overview:
    - Deposit ETH as collateral
    - Borrow USDC at optimal rates
    - Loop borrowed USDC to maximize yield while maintaining safe LTV
    - Monitor and adjust positions based on market conditions
    """
    
    def __init__(self, strategy_params: Dict[str, Any], settings: Any):
        super().__init__(strategy_params, settings)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.strategy_params = strategy_params
        self.settings = get_settings()
        
        # Strategy-specific parameters
        self.max_leverage = Decimal(strategy_params.get("max_leverage", "20.0"))
        self.target_ltv = Decimal(strategy_params.get("target_ltv", "0.75"))
        self.safety_buffer = Decimal(strategy_params.get("safety_buffer", "0.05"))
        self.min_apy_spread = Decimal(strategy_params.get("min_apy_spread", "0.02"))
        
        # Initialize CDP integration
        self.cdp_wrapper = CdpAgentkitWrapper(
            wallet_data=strategy_params.get("wallet_data"),
            api_key_name=self.settings.CDP_API_KEY_NAME,
            private_key=self.settings.CDP_API_KEY_PRIVATE_KEY
        )
        self._setup_cdp_tools()
        
        # Initialize strategy components
        self.data_collector = DataCollector(settings)
        self.decision_maker = DecisionMaker(settings)
        self.emergency_handler = EmergencyHandler(settings)
        self.performance_monitor = PerformanceMonitor()
        self.position_manager = PositionManager()
        self.risk_manager = RiskManager(settings)
        self.strategy_analyzer = StrategyAnalyzer(settings)
        
        # Market state
        self.market_data = {}
        self.current_position = None
        self.last_rebalance = None
        self.active_connections: Set[WebSocket] = set()

    def _setup_cdp_tools(self):
        """Initialize CDP toolkit and Morpho-specific tools"""
        cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(self.cdp_wrapper)
        self.tools = cdp_toolkit.get_tools()
        
        # Add Morpho-specific tools
        morpho_tools = [
            self._create_morpho_tool("morpho_borrow", MorphoBorrowInput, morpho_borrow),
            self._create_morpho_tool("morpho_leverage", MorphoLeverageInput, morpho_leverage),
            self._create_morpho_tool("morpho_repay", MorphoRepayInput, morpho_repay)
        ]
        self.tools.extend(morpho_tools)

    def _create_morpho_tool(self, name: str, input_schema: Any, func: Any):
        """Create a Morpho-specific CDP tool"""
        return CdpTool(
            name=name,
            description=f"Execute {name} operation on Morpho",
            cdp_agentkit_wrapper=self.cdp_wrapper,
            args_schema=input_schema,
            func=func
        )
    
    async def initialize(self) -> bool:
        """Initialize the agent by validating the market data feed and preloading market data."""
        try:
            await self.price_feed.validate_connection()
            self.market_data = await self.data_collector.fetch_market_data()
            self.logger.info("Morpho Agent initialized successfully.")
            return True
        except Exception as e:
            self.logger.error(f"Initialization failed: {str(e)}")
            await self.emergency_handler.handle_emergency(e)
            return False
    
    async def analyze_market(self) -> Dict[str, Any]:
        """
        Analyze market conditions for the ETH/USDC strategy:
        - ETH/USDC price and volatility
        - Morpho lending/borrowing rates
        - Market liquidity
        """
        try:
            market_data = await self.data_collector.fetch_market_data()
            
            # Analyze ETH/USDC specific metrics
            analysis = self.strategy_analyzer.analyze(market_data)
            risk_metrics = self.risk_manager.assess_risk(market_data)
            
            # Calculate current APY spread
            eth_supply_apy = Decimal(market_data.get("eth_supply_apy", 0))
            usdc_borrow_apy = Decimal(market_data.get("usdc_borrow_apy", 0))
            apy_spread = eth_supply_apy - usdc_borrow_apy
            
            analysis.update({
                "risk_metrics": risk_metrics,
                "apy_spread": float(apy_spread),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            self.market_data = analysis
            self.performance_monitor.record_metric("market_analysis", analysis)
            return analysis
            
        except Exception as e:
            self.logger.error(f"Market analysis error: {str(e)}")
            await self.emergency_handler.handle_emergency(e)
            return {}
    
    async def make_decision(self) -> Dict[str, Any]:
        """
        Make strategy decisions based on:
        - Current position LTV
        - APY spread
        - Risk metrics
        - Gas costs
        """
        try:
            if not self.market_data:
                await self.analyze_market()
            
            # Get current position metrics
            position_data = self.position_manager.get_position("current") if self.current_position else None
            current_ltv = Decimal(position_data.get("ltv", 0)) if position_data else Decimal(0)
            
            # Calculate optimal action based on strategy parameters
            apy_spread = Decimal(self.market_data.get("apy_spread", 0))
            risk_level = Decimal(self.market_data.get("risk_metrics", {}).get("total_risk", 1))
            
            decision = self.decision_maker.make_decision({
                "current_ltv": float(current_ltv),
                "target_ltv": float(self.target_ltv),
                "apy_spread": float(apy_spread),
                "risk_level": float(risk_level),
                "position_data": position_data,
                "market_data": self.market_data
            })
            
            self.logger.info(f"Strategy decision: {decision}")
            return decision
            
        except Exception as e:
            self.logger.error(f"Decision error: {str(e)}")
            await self.emergency_handler.handle_emergency(e)
            return {"action": "hold", "reason": str(e)}
    
    async def execute_trade(self, decision: Dict[str, Any]) -> bool:
        """Execute the strategy decision through Morpho protocol"""
        try:
            action = decision.get("action", "hold")
            
            if action == "hold":
                return True
                
            if action == "open_position":
                # Initial ETH deposit and USDC borrow
                result = await self.execute_borrow({
                    "collateral_token": "ETH",
                    "debt_token": "USDC",
                    "borrow_amount": decision.get("borrow_amount"),
                    "max_slippage": decision.get("max_slippage", 0.001)
                })
                if result.get("success"):
                    self.current_position = result
                    self.position_manager.open_position("current", result)
                return result.get("success", False)
                
            if action == "adjust_position":
                # Loop borrowed USDC
                result = await self.execute_leverage({
                    "position_id": self.current_position.get("id"),
                    "target_leverage": decision.get("target_leverage"),
                    "action_type": decision.get("action_type", "increase"),
                    "max_slippage": decision.get("max_slippage", 0.001)
                })
                if result.get("success"):
                    self.current_position.update(result)
                    self.position_manager.open_position("current", self.current_position)
                return result.get("success", False)
                
            if action == "close_position":
                result = await self.execute_repay({
                    "position_id": self.current_position.get("id"),
                    "repay_amount": decision.get("repay_amount"),
                    "withdraw_collateral": True,
                    "max_slippage": decision.get("max_slippage", 0.001)
                })
                if result.get("success"):
                    self.current_position = None
                    self.position_manager.close_position("current")
                return result.get("success", False)
                
            return False
            
        except Exception as e:
            self.logger.error(f"Trade execution error: {str(e)}")
            await self.emergency_handler.handle_emergency(e)
            return False
    
    # --- CDP AgentKit Action Methods ---
    async def execute_borrow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute borrow via CDP AgentKit's morpho_borrow tool."""
        try:
            borrow_input = MorphoBorrowInput(**params)
            borrow_tool = next(tool for tool in self.tools if tool.name == "morpho_borrow")
            result = await borrow_tool.arun(
                collateral_token=borrow_input.collateral_token,
                debt_token=borrow_input.debt_token,
                borrow_amount=borrow_input.borrow_amount,
                max_slippage=borrow_input.max_slippage
            )
            self.logger.info(f"Borrow result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error executing borrow: {str(e)}")
            raise
    
    async def execute_leverage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute leverage adjustment via CDP AgentKit's morpho_leverage tool."""
        try:
            leverage_input = MorphoLeverageInput(**params)
            leverage_tool = next(tool for tool in self.tools if tool.name == "morpho_leverage")
            result = await leverage_tool.arun(
                position_id=leverage_input.position_id,
                target_leverage=leverage_input.target_leverage,
                action_type=leverage_input.action_type,
                max_slippage=leverage_input.max_slippage
            )
            self.logger.info(f"Leverage result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error executing leverage: {str(e)}")
            raise
    
    async def execute_repay(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute repay via CDP AgentKit's morpho_repay tool."""
        try:
            repay_input = MorphoRepayInput(**params)
            repay_tool = next(tool for tool in self.tools if tool.name == "morpho_repay")
            result = await repay_tool.arun(
                position_id=repay_input.position_id,
                repay_amount=repay_input.repay_amount,
                withdraw_collateral=repay_input.withdraw_collateral,
                max_slippage=repay_input.max_slippage
            )
            self.logger.info(f"Repay result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error executing repay: {str(e)}")
            raise

    async def connect_client(self, websocket: WebSocket):
        """Handle new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        
    async def disconnect_client(self, websocket: WebSocket):
        """Handle WebSocket disconnection"""
        self.active_connections.remove(websocket)
        
    async def broadcast_message(self, message_type: MessageType, data: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        message = {
            "type": message_type.value,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        for connection in self.active_connections:
            await connection.send_json(message)

    async def run(self):
        """Main strategy loop"""
        if not await self.initialize():
            self.logger.error("Strategy initialization failed")
            return
            
        try:
            while True:
                # Analyze market and current position
                analysis = await self.analyze_market()
                
                # Check if emergency conditions exist
                if analysis.get("risk_metrics", {}).get("total_risk", 0) > 0.8:
                    await self.emergency_handler.handle_emergency(
                        Exception("Risk threshold exceeded")
                    )
                    continue
                
                # Make and execute strategy decisions
                decision = await self.make_decision()
                await self.execute_trade(decision)
                
                # Record performance metrics
                self.performance_monitor.record_metric(
                    "strategy_iteration",
                    {
                        "timestamp": datetime.utcnow().isoformat(),
                        "analysis": analysis,
                        "decision": decision,
                        "position": self.current_position
                    }
                )
                
                # Wait for next iteration
                await asyncio.sleep(self.strategy_params.get("poll_interval", 60))
                
        except Exception as e:
            self.logger.error(f"Strategy execution error: {str(e)}")
            await self.emergency_handler.handle_emergency(e) 
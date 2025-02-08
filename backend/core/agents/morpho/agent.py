from datetime import datetime
from typing import Dict, Any, Optional, Set, List

from cdp import Wallet
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

class MessageType(Enum):
    STRATEGY_SELECT = "strategy_select"
    MARKET_UPDATE = "market_update"
    POSITION_UPDATE = "position_update"
    ERROR = "error"
    ACTION_RESULT = "action_result"

class MorphoAgent(BaseAgent):
    """
    Enhanced Morpho protocol agent with CDP AgentKit integration.
    Combines LLM capabilities with onchain execution.
    """
    
    def __init__(self, strategy_params: Dict[str, Any], settings: Any):
        super().__init__(strategy_params, settings)
        self.price_feed = None
        self.cdp_wrapper = None
        self.llm = None
        self.tools = None
        self.memory = None
        self.active_connections: Set[WebSocket] = set()
        
        # Strategy-specific limits
        self.position_limits = {
            "max_leverage": strategy_params.get("max_leverage", 3.0),
            "min_collateral_ratio": strategy_params.get("min_collateral_ratio", 1.5),
            "max_position_size": strategy_params.get("max_position_size", 1000000)
        }

    async def initialize(self) -> bool:
        """Initialize agent with CDP AgentKit and other services"""
        try:
            # Initialize LLM
            self.llm = ChatOpenAI(model=self.settings.LLM_MODEL)
            self.memory = MemorySaver()
            
            # Initialize CDP AgentKit
            self.cdp_wrapper = CdpAgentkitWrapper(
                wallet_data=self.strategy_params.get("wallet_data")
            )
            
            # Initialize CDP toolkit and tools
            cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(self.cdp_wrapper)
            self.tools = cdp_toolkit.get_tools()
            
            # Add custom Morpho tools
            morpho_tools = [
                CdpTool(
                    name="morpho_borrow",
                    description=MORPHO_BORROW_PROMPT,
                    cdp_agentkit_wrapper=self.cdp_wrapper,
                    args_schema=MorphoBorrowInput,
                    func=morpho_borrow
                ),
                CdpTool(
                    name="morpho_leverage",
                    description=MORPHO_LEVERAGE_PROMPT,
                    cdp_agentkit_wrapper=self.cdp_wrapper,
                    args_schema=MorphoLeverageInput,
                    func=morpho_leverage
                ),
                CdpTool(
                    name="morpho_repay",
                    description=MORPHO_REPAY_PROMPT,
                    cdp_agentkit_wrapper=self.cdp_wrapper,
                    args_schema=MorphoRepayInput,
                    func=morpho_repay
                )
            ]
            
            # Add to existing tools
            self.tools.extend(morpho_tools)
            
            # Initialize other services
            self.price_feed = PriceFeed(
                api_key=self.settings.PRICE_FEED_API_KEY
            )
            
            # Validate connections
            await asyncio.gather(
                self.price_feed.validate_connection()
            )
            
            self.logger.info("Successfully initialized Morpho agent with CDP AgentKit")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Morpho agent: {str(e)}")
            return False
    
    async def analyze_market(self) -> Dict[str, Any]:
        """Enhanced market analysis with LLM insights"""
        try:
            # Get base market data (from original implementation)
            market_data = await self._get_base_market_data()
            
            # Get LLM analysis of market conditions
            llm_analysis = await self._get_llm_market_analysis(market_data)
            
            # Combine traditional and LLM analysis
            analysis = {
                **market_data,
                "llm_insights": llm_analysis,
                "market_sentiment": self._calculate_market_sentiment(market_data),
                "opportunity_score": self._calculate_opportunity_score(
                    market_data,
                    llm_analysis
                ),
                "risk_metrics": await self._calculate_risk_metrics(
                    market_data,
                    llm_analysis
                )
            }
            
            # Broadcast market update to connected clients
            await self.broadcast_message(
                MessageType.MARKET_UPDATE,
                {"analysis": analysis}
            )
            
            self.market_data = analysis
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in market analysis: {str(e)}")
            raise

    async def _get_llm_market_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get market analysis from LLM"""
        try:
            prompt = self._create_market_analysis_prompt(market_data)
            
            response = await self.llm.apredict(
                messages=[HumanMessage(content=prompt)]
            )
            
            # Parse LLM response into structured format
            analysis = self._parse_llm_analysis(response)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error getting LLM market analysis: {str(e)}")
            return {"error": str(e)}

    async def make_decision(self) -> Dict[str, Any]:
        """Enhanced decision making with CDP AgentKit and LLM"""
        try:
            if not self.market_data:
                await self.analyze_market()
            
            # Get base decision metrics
            opportunity_score = self.market_data["opportunity_score"]
            risk_metrics = self.market_data["risk_metrics"]
            llm_insights = self.market_data["llm_insights"]
            
            # Use CDP AgentKit to validate potential actions
            valid_actions = await self.cdp_wrapper.get_valid_actions(
                self.market_data
            )
            
            # Get LLM recommendation
            llm_recommendation = await self._get_llm_trade_recommendation(
                self.market_data,
                valid_actions
            )
            
            # Combine traditional and LLM-based decision making
            decision = await self._combine_decision_sources(
                opportunity_score,
                risk_metrics,
                llm_recommendation,
                valid_actions
            )
            
            # Broadcast decision to connected clients
            await self.broadcast_message(
                MessageType.ACTION_RESULT,
                {"decision": decision}
            )
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Error in decision making: {str(e)}")
            raise

    async def _combine_decision_sources(
        self,
        opportunity_score: float,
        risk_metrics: Dict[str, float],
        llm_recommendation: Dict[str, Any],
        valid_actions: List[str]
    ) -> Dict[str, Any]:
        """Combine different decision sources into final decision"""
        try:
            # Default to hold if no clear decision
            decision = {
                "action": "hold",
                "size": 0,
                "leverage": 1,
                "reason": "No clear action determined"
            }
            
            # Check if LLM recommendation is valid
            if (llm_recommendation["action"] in valid_actions and
                opportunity_score > self.settings.MIN_OPPORTUNITY_SCORE and
                risk_metrics["total_risk"] < self.settings.MAX_RISK_THRESHOLD):
                
                decision = llm_recommendation
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Error combining decisions: {str(e)}")
            return {"action": "hold", "reason": f"Error in decision making: {str(e)}"}
    
    async def execute_trade(self, decision: Dict[str, Any]) -> bool:
        """Execute the trading decision"""
        try:
            if decision["action"] == "hold":
                return True
                
            if decision["action"] == "open_long":
                success = await self.cdp_wrapper.open_position(
                    size=decision["size"],
                    leverage=decision["leverage"],
                    position_type="long"
                )
                
                if success:
                    self.current_position = {
                        "type": "long",
                        "size": decision["size"],
                        "leverage": decision["leverage"],
                        "entry_price": self.market_data["price_data"]["price"]
                    }
                    
            elif decision["action"] == "adjust_position":
                success = await self.cdp_wrapper.adjust_position(
                    position_id=self.current_position["id"],
                    size_delta=decision["size_delta"]
                )
                
                if success:
                    self.current_position["size"] += decision["size_delta"]
                    
            return success
            
        except Exception as e:
            self.logger.error(f"Error executing trade: {str(e)}")
            await self.handle_error(e)
            return False
    
    async def handle_error(self, error: Exception) -> None:
        """Handle errors during agent operation"""
        self.logger.error(f"Agent error: {str(error)}")
        
        if "insufficient_funds" in str(error).lower():
            await self.stop()
            self.logger.critical("Stopping agent due to insufficient funds")
        elif "connection" in str(error).lower():
            # Attempt to reconnect
            await self.initialize()
        else:
            # Log error and continue operation
            self.logger.warning("Continuing operation after error")
    
    def _calculate_market_sentiment(self, market_data: Dict[str, Any]) -> float:
        """Calculate market sentiment score"""
        try:
            price_change = market_data["change_24h"]
            volume = market_data["volume_24h"]
            # Implement sentiment calculation logic
            return 0.5  # Placeholder
        except Exception as e:
            self.logger.error(f"Error calculating market sentiment: {str(e)}")
            return 0.0
    
    def _calculate_opportunity_score(
        self,
        market_data: Dict[str, Any],
        morpho_data: Dict[str, Any]
    ) -> float:
        """Calculate opportunity score based on market and protocol data"""
        try:
            # Implement opportunity scoring logic
            return 0.5  # Placeholder
        except Exception as e:
            self.logger.error(f"Error calculating opportunity score: {str(e)}")
            return 0.0
    
    def _calculate_risk_metrics(
        self,
        market_data: Dict[str, Any],
        morpho_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate risk metrics"""
        try:
            return {
                "market_risk": 0.3,  # Placeholbr
                "protocol_risk": 0.2,  # Placeholder
                "total_risk": 0.25  # Placeholder
            }
        except Exception as e:
            self.logger.error(f"Error calculating risk metrics: {str(e)}")
            return {"total_risk": 1.0}  # Conservative default
    
    def _calculate_position_size(self) -> float:
        """Calculate appropriate position size based on strategy parameters"""
        try:
            available_capital = float(self.strategy_params["initial_capital"])
            risk_per_trade = 0.02  # 2% risk per trade
            return available_capital * risk_per_trade
        except Exception as e:
            self.logger.error(f"Error calculating position size: {str(e)}")
            return 0.0
    
    def _calculate_leverage(self) -> float:
        """Calculate appropriate leverage based on market conditions"""
        try:
            base_leverage = 2.0
            market_volatility = 0.5  # Placeholder
            return min(
                base_leverage * (1 - market_volatility),
                self.position_limits["max_leverage"]
            )
        except Exception as e:
            self.logger.error(f"Error calculating leverage: {str(e)}")
            return 1.0
    
    def _calculate_position_adjustment(self) -> float:
        """Calculate position size adjustment"""
        try:
            if not self.current_position:
                return 0.0
            
            # Implement position adjustment logic
            return 0.0  # Placeholder
        except Exception as e:
            self.logger.error(f"Error calculating position adjustment: {str(e)}")
            return 0.0 

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

    async def execute_borrow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute borrow action through CDP AgentKit"""
        try:
            # Validate parameters
            borrow_input = MorphoBorrowInput(**params)
            
            # Get borrow tool
            borrow_tool = next(
                tool for tool in self.tools 
                if tool.name == "morpho_borrow"
            )
            
            # Execute borrow through CDP
            result = await borrow_tool.arun(
                collateral_token=borrow_input.collateral_token,
                debt_token=borrow_input.debt_token,
                borrow_amount=borrow_input.borrow_amount,
                max_slippage=borrow_input.max_slippage
            )
            
            # Broadcast result to connected clients
            await self.broadcast_message(
                MessageType.ACTION_RESULT,
                {"action": "borrow", "result": result}
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing borrow: {str(e)}")
            raise

    async def _get_llm_trade_recommendation(
        self,
        market_data: Dict[str, Any],
        valid_actions: List[str]
    ) -> Dict[str, Any]:
        """Get trade recommendation from LLM"""
        try:
            # Create prompt for LLM
            prompt = self._create_trade_recommendation_prompt(
                market_data,
                valid_actions
            )
            
            # Get LLM response
            response = await self.llm.apredict(
                messages=[HumanMessage(content=prompt)]
            )
            
            # Parse recommendation
            recommendation = self._parse_llm_recommendation(response)
            
            # Handle different action types
            action = recommendation.get("action")
            params = recommendation.get("params", {})
            
            if action == "borrow":
                await self.execute_borrow(params)
            elif action == "leverage":
                await self.execute_leverage(params)
            elif action == "repay":
                await self.execute_repay(params)
            
            return recommendation
            
        except Exception as e:
            self.logger.error(f"Error getting LLM recommendation: {str(e)}")
            return {"error": str(e)}

    async def execute_leverage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute leverage adjustment through CDP AgentKit"""
        try:
            # Validate parameters
            leverage_input = MorphoLeverageInput(**params)
            
            # Get leverage tool
            leverage_tool = next(
                tool for tool in self.tools 
                if tool.name == "morpho_leverage"
            )
            
            # Execute leverage through CDP
            result = await leverage_tool.arun(
                position_id=leverage_input.position_id,
                target_leverage=leverage_input.target_leverage,
                action_type=leverage_input.action_type,
                max_slippage=leverage_input.max_slippage
            )
            
            # Broadcast result to connected clients
            await self.broadcast_message(
                MessageType.ACTION_RESULT,
                {"action": "leverage", "result": result}
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing leverage adjustment: {str(e)}")
            raise

    async def execute_repay(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute repay action through CDP AgentKit"""
        try:
            # Validate parameters
            repay_input = MorphoRepayInput(**params)
            
            # Get repay tool
            repay_tool = next(
                tool for tool in self.tools 
                if tool.name == "morpho_repay"
            )
            
            # Execute repay through CDP
            result = await repay_tool.arun(
                position_id=repay_input.position_id,
                repay_amount=repay_input.repay_amount,
                withdraw_collateral=repay_input.withdraw_collateral,
                max_slippage=repay_input.max_slippage
            )
            
            # Broadcast result to connected clients
            await self.broadcast_message(
                MessageType.ACTION_RESULT,
                {"action": "repay", "result": result}
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing repay: {str(e)}")
            raise

    async def execute_deposit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute deposit action through CDP AgentKit"""
        try:
            # Validate parameters
            deposit_input = MorphoDepositInput(**params)
            
            # Get deposit tool
            deposit_tool = next(
                tool for tool in self.tools 
                if tool.name == "morpho_deposit"
            )
            
            # Execute deposit through CDP
            result = await deposit_tool.arun(
                vault_address=deposit_input.vault_address,
                assets=deposit_input.assets,
                receiver=deposit_input.receiver,
                token_address=deposit_input.token_address
            )
            
            # Broadcast result to connected clients
            await self.broadcast_message(
                MessageType.ACTION_RESULT,
                {"action": "deposit", "result": result}
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing deposit: {str(e)}")
            raise

    async def execute_withdraw(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute withdraw action through CDP AgentKit"""
        try:
            # Validate parameters
            withdraw_input = MorphoWithdrawInput(**params)
            
            # Get withdraw tool
            withdraw_tool = next(
                tool for tool in self.tools 
                if tool.name == "morpho_withdraw"
            )
            
            # Execute withdraw through CDP
            result = await withdraw_tool.arun(
                vault_address=withdraw_input.vault_address,
                assets=withdraw_input.assets,
                receiver=withdraw_input.receiver
            )
            
            # Broadcast result to connected clients
            await self.broadcast_message(
                MessageType.ACTION_RESULT,
                {"action": "withdraw", "result": result}
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing withdraw: {str(e)}")
            raise 
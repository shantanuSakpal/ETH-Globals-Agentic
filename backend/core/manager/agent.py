from typing import Dict
from backend.config import settings
from backend.core.agents.morpho.agent import MorphoAgent
import asyncio
import logging

class AgentManager:
    def __init__(self):
        self.agents: Dict[str, MorphoAgent] = {}
        self.logger = logging.getLogger(__name__)

    async def initialize(self):
        """Initialize the agent manager"""
        self.logger.info("Initializing agent manager")

    async def run_agents(self):
        """Run all active agents"""
        while True:
            for agent_id, agent in self.agents.items():
                try:
                    await agent.analyze_market()
                    decision = await agent.make_decision()
                    if decision.get("action") != "hold":
                        await agent.execute_trade(decision)
                except Exception as e:
                    self.logger.error(f"Error in agent {agent_id}: {str(e)}")
            await asyncio.sleep(60)

    async def add_agent(self, agent_id: str, strategy_params: dict) -> bool:
        """Add and initialize a new agent"""
        try:
            agent = MorphoAgent(strategy_params=strategy_params, settings=settings)
            if await agent.initialize():
                self.agents[agent_id] = agent
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error adding agent: {str(e)}")
            return False

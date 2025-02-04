from agents.morpho_agent import MorphoAgent
from config.settings import get_settings
import asyncio
import logging
from datetime import datetime

async def run_agent_loop(agent: MorphoAgent, interval: int = 60):
    """Run the Morpho agent main loop"""
    while True:
        try:
            # Market analysis
            await agent.analyze_market()
            
            # Make trading decision
            decision = await agent.make_decision()
            
            # Execute if needed
            if decision.get("action") != "hold":
                await agent.execute_trade(decision)
                
            await asyncio.sleep(interval)
            
        except Exception as e:
            logging.error(f"Error in agent loop: {str(e)}")
            await agent.handle_error(e)
            await asyncio.sleep(interval)

async def main():
    settings = get_settings()
    
    # Initialize agent
    agent = MorphoAgent(
        strategy_params={
            "max_leverage": 3.0,
            "min_collateral_ratio": 1.5,
            "max_position_size": 1000000,
            "wallet_data": {
                "address": settings.WALLET_ADDRESS,
                "private_key": settings.WALLET_PRIVATE_KEY
            }
        },
        settings=settings
    )
    
    if not await agent.initialize():
        logging.error("Failed to initialize agent")
        return
        
    await run_agent_loop(agent)

if __name__ == "__main__":
    asyncio.run(main())

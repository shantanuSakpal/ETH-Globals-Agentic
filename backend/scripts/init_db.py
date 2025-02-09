from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from config.settings import get_settings

async def init_database():
    settings = get_settings()
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client.helenus2
    
    # Create collections
    await db.create_collection("vaults")
    await db.create_collection("strategies")
    await db.create_collection("positions")
    await db.create_collection("wallets")
    
    # Create indexes
    await db.vaults.create_index("user_id")
    await db.vaults.create_index("strategy_id")
    await db.strategies.create_index("user_id")
    await db.positions.create_index("vault_id")
    await db.wallets.create_index("id")
    await db.wallets.create_index("user_id")
    
    print("Database initialized successfully!")

if __name__ == "__main__":
    asyncio.run(init_database())

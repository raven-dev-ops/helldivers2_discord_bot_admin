import logging
from motor.motor_asyncio import AsyncIOMotorClient
from config import mongo_uri

client = None

async def get_mongo_client():
    """Retrieve or initialize the MongoDB client."""
    global client
    if client is None:
        client = AsyncIOMotorClient(mongo_uri)
    return client

# Function to create indexes for performance optimization
async def create_indexes():
    """Creates necessary indexes for MongoDB collections."""
    try:
        mongo_client = await get_mongo_client()
        db = mongo_client['GPTHellbot']
        stats_collection = db['User_Stats']
        alliance_collection = db['Alliance']
        server_listing_collection = db['Server_Listing']

        # Create indexes
        await stats_collection.create_index("server_nickname")
        await alliance_collection.create_index("player_name")
        await alliance_collection.create_index("discord_id")
        await alliance_collection.create_index("discord_server_id")
        await server_listing_collection.create_index("discord_server_id")
        logging.info("Created indexes on 'Nickname', 'player_name', 'discord_id', and 'discord_server_id'.")
    except Exception as e:
        logging.error(f"Error creating indexes: {e}")

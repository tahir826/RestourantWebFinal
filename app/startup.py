from app.config import DB_CONNECTION_STRING
from app.db import Database

async def startup():
    """Create the database pool on app startup."""
    await Database.connect(DB_CONNECTION_STRING)

async def shutdown():
    """Release the database pool on app shutdown."""
    await Database.disconnect()
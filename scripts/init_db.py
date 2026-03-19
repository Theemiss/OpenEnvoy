#!/usr/bin/env python3
"""Database initialization script."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.core.database import db_manager, Base
from backend.core.config import settings
from backend.models import *  # Import all models


async def create_tables():
    """Create all database tables."""
    print(f"Connecting to database: {settings.DATABASE_URL}")
    
    await db_manager.initialize()
    
    async with db_manager.engine.begin() as conn:
        print("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
    
    print("Tables created successfully!")
    await db_manager.close()


async def drop_tables():
    """Drop all database tables."""
    print(f"WARNING: This will drop all tables in {settings.DATABASE_URL}")
    response = input("Are you sure? (yes/no): ")
    
    if response.lower() != "yes":
        print("Aborted.")
        return
    
    await db_manager.initialize()
    
    async with db_manager.engine.begin() as conn:
        print("Dropping tables...")
        await conn.run_sync(Base.metadata.drop_all)
    
    print("Tables dropped successfully!")
    await db_manager.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database management")
    parser.add_argument("action", choices=["create", "drop", "reset"])
    
    args = parser.parse_args()
    
    if args.action == "create":
        asyncio.run(create_tables())
    elif args.action == "drop":
        asyncio.run(drop_tables())
    elif args.action == "reset":
        asyncio.run(drop_tables())
        asyncio.run(create_tables())
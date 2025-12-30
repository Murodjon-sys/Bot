#!/usr/bin/env python3
"""
Database migration: Add payments table
"""
import asyncio
from sqlalchemy import text
from db.database import async_session, engine
from db.models import Base

async def migrate():
    """Add payments table to database"""
    print("🔄 Migration: Adding payments table...")
    
    # Create all tables (including new Payment table)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Migration completed successfully!")
    print("   - payments table created")

if __name__ == "__main__":
    asyncio.run(migrate())

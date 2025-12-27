"""
Database migration: Add language column to users table
"""
import asyncio
from sqlalchemy import text
from db.database import async_session

async def migrate():
    """Add language column to users table"""
    async with async_session() as session:
        try:
            # Check if column exists
            result = await session.execute(
                text("PRAGMA table_info(users)")
            )
            columns = result.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'language' not in column_names:
                print("Adding language column...")
                await session.execute(
                    text("ALTER TABLE users ADD COLUMN language VARCHAR DEFAULT 'uz' NOT NULL")
                )
                await session.commit()
                print("✅ Language column added successfully!")
            else:
                print("✅ Language column already exists")
                
        except Exception as e:
            print(f"❌ Migration error: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(migrate())

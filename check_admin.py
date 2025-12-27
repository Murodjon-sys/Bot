#!/usr/bin/env python3
"""Check if admin user exists in database"""
import asyncio
from sqlalchemy import select
from db.database import async_session
from db.models import User
from config import ADMIN_USERNAME

async def check_admin():
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.username == ADMIN_USERNAME)
        )
        admin = result.scalar_one_or_none()
        
        if admin:
            print(f"✅ Admin user topildi:")
            print(f"   Username: @{admin.username}")
            print(f"   Telegram ID: {admin.telegram_id}")
            print(f"   Language: {admin.language}")
        else:
            print(f"❌ Admin user topilmadi!")
            print(f"   ADMIN_USERNAME: {ADMIN_USERNAME}")
            print(f"\n💡 Yechim:")
            print(f"   1. Telegram botga @{ADMIN_USERNAME} akkauntidan /start bosing")
            print(f"   2. Yoki config.py da ADMIN_USERNAME ni to'g'ri username ga o'zgartiring")

if __name__ == "__main__":
    asyncio.run(check_admin())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database ni tozalash (faqat yangiliklar va userlar)
"""
import asyncio
from sqlalchemy import select, delete
from db.database import async_session, init_db
from db.models import News, User, UserInterest

async def clear_database():
    """Yangiliklar va userlar ni o'chirish (kanallar saqlanadi)"""
    await init_db()
    
    print("🗑️ Database tozalanmoqda...")
    
    async with async_session() as session:
        # Barcha ma'lumotlar sonini olish
        result_news = await session.execute(select(News))
        news_count = len(result_news.scalars().all())
        
        result_users = await session.execute(select(User))
        users_count = len(result_users.scalars().all())
        
        result_interests = await session.execute(select(UserInterest))
        interests_count = len(result_interests.scalars().all())
        
        print(f"📊 O'chiriladigan ma'lumotlar:")
        print(f"   - {news_count} ta yangilik")
        print(f"   - {users_count} ta user")
        print(f"   - {interests_count} ta qiziqish")
        print(f"\nℹ️ Kanallar SAQLANADI (o'chirilmaydi)")
        
        if news_count == 0 and users_count == 0:
            print("\n✅ Database allaqachon bo'sh")
            return
        
        # Tasdiqlash
        confirm = input("\n⚠️ Yangiliklar va userlar o'chiriladi. Davom etasizmi? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("❌ Bekor qilindi")
            return
        
        # Faqat yangiliklar va userlar ni o'chirish
        await session.execute(delete(UserInterest))  # Avval qiziqishlar (foreign key)
        await session.execute(delete(News))
        await session.execute(delete(User))
        await session.commit()
        
        print(f"\n✅ Database tozalandi!")
        print(f"   - {news_count} ta yangilik o'chirildi")
        print(f"   - {users_count} ta user o'chirildi")
        print(f"   - {interests_count} ta qiziqish o'chirildi")
        print(f"\n📋 Kanallar saqlanib qoldi")

if __name__ == "__main__":
    asyncio.run(clear_database())

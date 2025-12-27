#!/usr/bin/env python3
"""Check media in database"""
import asyncio
from sqlalchemy import select
from db.database import async_session
from db.models import News

async def check_media():
    async with async_session() as session:
        # Barcha yangiliklar
        result = await session.execute(
            select(News).order_by(News.created_at.desc()).limit(20)
        )
        news_list = result.scalars().all()
        
        print(f"📰 Oxirgi 20 ta yangilik:\n")
        
        for news in news_list:
            media_info = "❌ Yo'q"
            if news.media_type:
                if news.media_file_id:
                    media_info = f"✅ {news.media_type} (file_id: {news.media_file_id[:30]}...)"
                else:
                    media_info = f"⚠️ {news.media_type} (file_id YO'Q!)"
            
            print(f"ID: {news.id}")
            print(f"   Kategoriya: {news.category}")
            print(f"   Text: {news.text[:50]}...")
            print(f"   Media: {media_info}")
            print(f"   Vaqt: {news.created_at}")
            print()

if __name__ == "__main__":
    asyncio.run(check_media())

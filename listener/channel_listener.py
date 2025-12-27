from telethon import TelegramClient, events
from config import API_ID, API_HASH, PHONE, CHANNELS_TO_MONITOR
from processor.text_cleaner import clean_text
from processor.classifier import classify_news
import asyncio

class ChannelListener:
    def __init__(self, news_callback):
        """
        news_callback: yangilik kelganda chaqiriladigan funksiya
        """
        self.client = TelegramClient('news_session', API_ID, API_HASH)
        self.news_callback = news_callback
    
    async def start(self):
        """Listener ni ishga tushirish"""
        await self.client.start(phone=PHONE)
        print("✅ Channel listener ishga tushdi")
        
        # Bot ishga tushganda oxirgi 24 soatdagi yangiliklar ni olish
        await self._fetch_recent_messages()
        
        # Kanallarni kuzatish
        @self.client.on(events.NewMessage(chats=CHANNELS_TO_MONITOR))
        async def handler(event):
            # Text yoki caption olish
            raw_text = None
            
            # Oddiy text post
            if event.message.text:
                raw_text = event.message.text
            # Video/photo caption
            elif event.message.message:
                raw_text = event.message.message
            
            # Agar text yo'q bo'lsa - o'tkazib yuborish
            if not raw_text or len(raw_text.strip()) < 10:
                return
            
            channel = await event.get_chat()
            
            # Media olish (photo/video) - Telegram message object ni uzatish
            media = None
            if event.message.photo:
                media = {
                    'type': 'photo',
                    'message': event.message  # To'liq message object
                }
            elif event.message.video:
                media = {
                    'type': 'video',
                    'message': event.message  # To'liq message object
                }
            
            # Tozalash va klassifikatsiya
            cleaned = clean_text(raw_text)
            category = classify_news(cleaned, channel.username)
            
            # Debug log
            print(f"\n📨 Yangi xabar: @{channel.username}")
            print(f"   Text: {raw_text[:100]}...")
            print(f"   Media: {media['type'] if media else 'Yo\'q'}")
            print(f"   Kategoriya: {category}")
            
            # Callback ga yuborish
            await self.news_callback(
                channel_username=channel.username,
                message_id=event.message.id,
                text=cleaned,
                category=category,
                raw_text=raw_text,
                media=media
            )
        
        print(f"📡 Kuzatilayotgan kanallar: {', '.join(CHANNELS_TO_MONITOR)}")
        await self.client.run_until_disconnected()
    
    async def _fetch_recent_messages(self):
        """Bot ishga tushganda barcha kategoriyalar uchun eng oxirgi yangiliklar ni olish"""
        from datetime import datetime, timedelta, timezone
        from config import CATEGORIES
        
        print("\n🔄 Barcha kategoriyalar uchun eng oxirgi yangiliklar yuklanmoqda...")
        print("   ℹ️ Har bir kategoriyadan eng oxirgi 1 ta yangilik yuklanadi")
        print(f"   📋 Kategoriyalar: {', '.join(CATEGORIES.keys())}")
        
        # Har bir kategoriya uchun eng oxirgi yangilikni saqlash
        latest_by_category = {}
        
        # Barcha kategoriyalarni boshlang'ich qiymat bilan to'ldirish
        for category in CATEGORIES.keys():
            latest_by_category[category] = None
        
        for channel_username in CHANNELS_TO_MONITOR:
            try:
                # Kanalni olish
                channel = await self.client.get_entity(channel_username)
                
                # Oxirgi 100 ta xabarni olish (barcha kategoriyalar uchun)
                print(f"\n   🔍 @{channel_username}: oxirgi 100 ta post tekshirilmoqda...")
                messages = await self.client.get_messages(channel, limit=100)
                
                processed_count = 0
                
                for message in messages:
                    # Text olish
                    raw_text = None
                    if message.text:
                        raw_text = message.text
                    elif message.message:
                        raw_text = message.message
                    
                    if not raw_text or len(raw_text.strip()) < 10:
                        continue
                    
                    # Media olish - Telegram message object ni uzatish
                    media = None
                    if message.photo:
                        media = {
                            'type': 'photo',
                            'message': message  # To'liq message object
                        }
                    elif message.video:
                        media = {
                            'type': 'video',
                            'message': message  # To'liq message object
                        }
                    
                    # Tozalash va klassifikatsiya
                    cleaned = clean_text(raw_text)
                    category = classify_news(cleaned, channel.username)
                    
                    # Agar kategoriya topilmasa - o'tkazib yuborish
                    if not category or category == 'other':
                        continue
                    
                    processed_count += 1
                    
                    # Har bir kategoriyadan eng oxirgi yangilikni saqlash
                    # YANGI MANTIQ: Har doim eng oxirgi yangilikni olish (media bor yoki yo'q)
                    # Agar kategoriya hali bo'sh bo'lsa - qo'shish
                    if latest_by_category[category] is None:
                        latest_by_category[category] = {
                            'channel_username': channel.username,
                            'message_id': message.id,
                            'text': cleaned,
                            'category': category,
                            'raw_text': raw_text,
                            'media': media,
                            'date': message.date
                        }
                        media_status = f"({media['type']})" if media else "(media yo'q)"
                        print(f"      ✅ {category}: yangilik topildi {media_status}")
                    # Agar kategoriya bor lekin media yo'q bo'lsa - media bilan yangilikni qo'yish
                    elif latest_by_category[category]['media'] is None and media is not None:
                        latest_by_category[category] = {
                            'channel_username': channel.username,
                            'message_id': message.id,
                            'text': cleaned,
                            'category': category,
                            'raw_text': raw_text,
                            'media': media,
                            'date': message.date
                        }
                        print(f"      🎥 {category}: media bilan yangilik topildi ({media['type']})")
                
                print(f"      📊 Jami {processed_count} ta yangilik qayta ishlandi")
                
            except Exception as e:
                print(f"   ❌ @{channel_username}: {e}")
        
        # Endi har bir kategoriyadan eng oxirgi 1 tasini yuborish
        print(f"\n   📊 NATIJA:")
        total_processed = 0
        
        for category in CATEGORIES.keys():
            news_data = latest_by_category.get(category)
            
            if news_data:
                print(f"      ✅ {category}: yangilik yuborilmoqda...")
                
                # Callback ga yuborish
                await self.news_callback(
                    channel_username=news_data['channel_username'],
                    message_id=news_data['message_id'],
                    text=news_data['text'],
                    category=news_data['category'],
                    raw_text=news_data['raw_text'],
                    media=news_data['media']
                )
                
                total_processed += 1
                
                # Spam oldini olish uchun pauza
                await asyncio.sleep(0.5)
            else:
                print(f"      ⚠️ {category}: yangilik topilmadi")
        
        print(f"\n✅ Jami {total_processed}/{len(CATEGORIES)} ta kategoriya uchun yangilik yuklandi\n")
    
    async def stop(self):
        """Listener ni to'xtatish"""
        try:
            if self.client and self.client.is_connected():
                await self.client.disconnect()
        except Exception as e:
            print(f"⚠️ Listener to'xtatishda xato: {e}")

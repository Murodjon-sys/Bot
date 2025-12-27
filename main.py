import asyncio
import logging
from datetime import datetime
from sqlalchemy import select
from db.database import init_db, async_session
from db.models import News, Channel
from bot.bot import NewsBot
from listener.channel_listener import ChannelListener
from services.user_matcher import get_matching_users
from processor.text_cleaner import extract_preview, clean_text
from processor.language_detector import is_uzbek

# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global bot instance
bot = None

async def on_new_news(channel_username, message_id, text, category, raw_text, media=None):
    """
    Yangilik kelganda ishlaydigan callback
    media: {'type': 'photo'/'video', 'file': file_object}
    """
    print(f"\nðŸ“° Yangi post: @{channel_username}")
    print(f"   Kategoriya: {category}")
    print(f"   Text preview: {extract_preview(text, 100)}")
    media_status = f"✅ {media['type']}" if media else "❌ Yo'q"
    print(f"   Media: {media_status}")
    
    # Til tekshiruvi - faqat o'zbek tilida
    if not is_uzbek(raw_text):
        print(f"   ⚠️ O'zbek tilida emas, o'tkazib yuborildi")
        return
    
    # Kategoriya tekshiruvi - agar kategoriya topilmasa o'tkazib yuborish
    if not category or category == 'other':
        print(f"   ⚠️ Kategoriya aniqlanmadi, o'tkazib yuborildi")
        return
    
    # Database'ga saqlash
    from db.models import News, Channel, User
    async with async_session() as session:
        # Kanal olish yoki yaratish
        result = await session.execute(
            select(Channel).where(Channel.username == channel_username)
        )
        channel = result.scalar_one_or_none()
        
        if not channel:
            channel = Channel(username=channel_username)
            session.add(channel)
            await session.commit()
            await session.refresh(channel)
        
        # Duplicate tekshirish (oxirgi 12 soat)
        from datetime import timedelta
        recent_time = datetime.utcnow() - timedelta(hours=12)
        
        # Kanal nomlarini va ortiqcha matnlarni olib tashlash
        cleaned_text = clean_text(raw_text)
        
        # Birinchi 100 belgini tekshirish (cleaned_text dan)
        text_preview = cleaned_text[:100]
        result = await session.execute(
            select(News).where(
                News.channel_id == channel.id,
                News.message_id == message_id
            )
        )
        duplicate = result.scalar_one_or_none()
        
        if duplicate:
            print(f"   âš ï¸ Duplicate yangilik (oxirgi 12 soatda mavjud), o'tkazib yuborildi")
            return
        
        # Media file_id ni olish (agar bo'lsa)
        # YANGI YECHIM: Har doim media ni download qilish va file_id olish (eski yangiliklar uchun ham)
        media_type = None
        media_file_id = None
        
        if media and bot:
            media_type = media['type']
            
            # Photo uchun - file_id olish
            if media_type == 'photo':
                try:
                    # Media ni download qilish
                    from io import BytesIO
                    media_bytes = BytesIO()
                    await media['message'].download_media(media_bytes)
                    media_bytes.seek(0)
                    
                    print(f"   📥 Photo download qilindi: {len(media_bytes.getvalue())} bytes")
                    logger.info(f"Photo download qilindi: {len(media_bytes.getvalue())} bytes")
                    
                    # Admin ga yuborish va file_id olish
                    from config import ADMIN_USERNAME
                    result_admin = await session.execute(
                        select(User).where(User.username == ADMIN_USERNAME)
                    )
                    admin_user = result_admin.scalar_one_or_none()
                    
                    if admin_user:
                        try:
                            print(f"   📤 Admin ga yuborilmoqda (silent)...")
                            sent = await bot.app.bot.send_photo(
                                chat_id=admin_user.telegram_id,
                                photo=media_bytes,
                                caption="🔧 [TEXNIK] File ID olish uchun",
                                disable_notification=True  # Silent yuborish
                            )
                            if sent.photo:
                                media_file_id = sent.photo[-1].file_id
                                print(f"   ✅ Photo file_id olindi: {media_file_id[:30]}...")
                                
                                # Admin ga yuborilgan rasmni o'chirish (tozalash)
                                try:
                                    await bot.app.bot.delete_message(
                                        chat_id=admin_user.telegram_id,
                                        message_id=sent.message_id
                                    )
                                    print(f"   🗑️ Admin rasmni o'chirildi")
                                except:
                                    pass
                            else:
                                print(f"   ❌ sent.photo bo'sh!")
                        except Exception as e:
                            print(f"   ❌ Admin ga yuborishda xato: {e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        print(f"   ❌ Admin user topilmadi (username: {ADMIN_USERNAME})")
                            
                except Exception as e:
                    print(f"   ❌ Media download xato: {e}")
                    import traceback
                    traceback.print_exc()
            elif media_type == 'video':
                # Video yuklab olish va file_id olish (BARCHA videolar)
                try:
                    from io import BytesIO
                    
                    print(f"   📥 Video yuklab olinmoqda...")
                    
                    # Video yuklab olish (hajmidan qat'iy nazar)
                    media_bytes = BytesIO()
                    await media['message'].download_media(media_bytes)
                    media_bytes.seek(0)
                    
                    video_size = len(media_bytes.getvalue())
                    print(f"   📥 Video download qilindi: {video_size / (1024*1024):.2f} MB")
                    logger.info(f"Video download qilindi: {video_size} bytes")
                    
                    # Admin ga yuborish va file_id olish
                    from config import ADMIN_USERNAME
                    result_admin = await session.execute(
                        select(User).where(User.username == ADMIN_USERNAME)
                    )
                    admin_user = result_admin.scalar_one_or_none()
                    
                    if admin_user:
                        try:
                            print(f"   📤 Admin ga yuborilmoqda (silent)...")
                            sent = await bot.app.bot.send_video(
                                chat_id=admin_user.telegram_id,
                                video=media_bytes,
                                caption="🔧 [TEXNIK] File ID olish uchun",
                                disable_notification=True  # Silent yuborish
                            )
                            if sent.video:
                                media_file_id = sent.video.file_id
                                print(f"   ✅ Video file_id olindi: {media_file_id[:30]}...")
                                
                                # Admin ga yuborilgan videoni o'chirish (tozalash)
                                try:
                                    await bot.app.bot.delete_message(
                                        chat_id=admin_user.telegram_id,
                                        message_id=sent.message_id
                                    )
                                    print(f"   🗑️ Admin videoni o'chirildi")
                                except:
                                    pass
                            else:
                                print(f"   ❌ sent.video bo'sh!")
                        except Exception as e:
                            print(f"   ❌ Admin ga yuborishda xato: {e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        print(f"   ❌ Admin user topilmadi (username: {ADMIN_USERNAME})")
                            
                except Exception as e:
                    print(f"   ❌ Video download xato: {e}")
                    import traceback
                    traceback.print_exc()
        
        # Yangilikni saqlash (tozalangan matn va media bilan)
        # AVVAL: Agar media bo'lsa va file_id olindi bo'lsa - o'sha kategoriyaning eski media'larini o'chirish
        if media_file_id and media_type:
            # O'sha kategoriyaning eski media'larini topish (video yoki photo)
            result_old = await session.execute(
                select(News)
                .where(News.category == category)
                .where(News.media_type == media_type)
                .where(News.media_file_id.isnot(None))
                .order_by(News.created_at.desc())
            )
            old_media = result_old.scalars().all()
            
            if old_media:
                print(f"   🗑️ {category} kategoriyasida {len(old_media)} ta eski {media_type} topildi, o'chirilmoqda...")
                for old_item in old_media:
                    await session.delete(old_item)
                await session.commit()
                print(f"   ✅ Eski {media_type}lar o'chirildi")
        
        # KEYIN: Yangi yangilikni saqlash
        news = News(
            channel_id=channel.id,
            message_id=message_id,
            text=cleaned_text,  # Tozalangan matn (kanal nomsiz)
            category=category,
            media_type=media_type,
            media_file_id=media_file_id,
            channel_username=channel_username,  # Forward uchun
            channel_message_id=message_id  # Forward uchun
        )
        session.add(news)
        await session.commit()
        print(f"   ðŸ’¾ Database'ga saqlandi")
        
        # Mos userlarni topish (settings bilan)
        is_breaking = False  # TODO: AI dan olish kerak
        
        # Agar kategoriya "umumiy" bo'lsa - barcha aktiv userlarga yuborish
        if category == 'umumiy':
            from db.models import User
            result = await session.execute(
                select(User).where(
                    (User.trial_end > datetime.utcnow()) | (User.subscription_end > datetime.utcnow())
                )
            )
            users = result.scalars().all()
            matching_users = [user.telegram_id for user in users]
            print(f"   ðŸ“¢ Umumiy yangilik - barcha aktiv userlarga yuboriladi ({len(matching_users)} user)")
        else:
            matching_users = await get_matching_users(session, category, text, is_breaking)
            print(f"   ðŸ‘¥ {category} kategoriyasi uchun {len(matching_users)} user topildi")
        
        if not matching_users:
            print(f"   â„¹ï¸ Bu kategoriyaga qiziqadigan user yo'q")
            # Umumiy kategoriya bo'lsa ham yuborish
            if category == 'umumiy':
                print(f"   âš ï¸ Hech qanday aktiv user yo'q!")
            return
        
        print(f"   âœ‰ï¸ {len(matching_users)} ta userga yuborilmoqda...")
        
        # Har bir userga yuborish (tozalangan formatda, media bilan)
        # Agar media_file_id bo'lsa - file_id orqali yuborish
        # Agar media_file_id yo'q lekin media_type bor - forward qilish (katta videolar uchun)
        media_for_bot = None
        forward_info = None
        
        if media_file_id:
            # Kichik media - file_id orqali yuborish
            media_for_bot = {
                'type': media_type,
                'file_id': media_file_id
            }
        elif media_type:
            # Katta media (file_id yo'q) - forward qilish
            forward_info = {
                'channel': channel_username,
                'message_id': message_id
            }
            print(f"   📹 Video juda katta, forward orqali yuboriladi")
        
        for user_id in matching_users:
            await bot.send_news_to_user(
                telegram_id=user_id,
                news_text=cleaned_text,  # Tozalangan matn (kanal nomsiz)
                category=category,
                channel=channel_username,
                media=media_for_bot,  # Media (photo/video) file_id bilan
                forward_info=forward_info  # Forward ma'lumotlari (katta videolar uchun)
            )
        
        # Yuborilgan userlar sonini yangilash
        news.sent_count = len(matching_users)
        await session.commit()
        
        print(f"   âœ… Yuborildi!")

async def setup_menu():
    """Bot menu ni o'rnatish"""
    from telegram import BotCommand
    
    commands = [
        BotCommand("start", "🏠 Bosh sahifa"),
    ]
    
    await bot.app.bot.set_my_commands(commands)
    print("✅ Bot menu o'rnatildi")

async def main():
    """Asosiy funksiya"""
    global bot
    
    print("🚀 News Bot ishga tushmoqda...")
    
    # Database yaratish
    await init_db()
    print("✅ Database tayyor")
    
    # Bot yaratish
    bot = NewsBot()
    
    # Menu o'rnatish
    await setup_menu()
    
    # Listener yaratish
    listener = ChannelListener(news_callback=on_new_news)
    
    # Ikkalasini parallel ishga tushirish
    try:
        await asyncio.gather(
            bot.start(),
            listener.start()
        )
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\nâ¹ï¸ To'xtatilmoqda...")
    finally:
        try:
            await bot.stop()
            await listener.stop()
            print("âœ… Bot to'xtatildi")
        except:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nâœ… Dastur to'xtatildi")
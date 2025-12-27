from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import BOT_TOKEN
from bot.handlers import start_command, interest_callback, interests_command, status_command

class NewsBot:
    def __init__(self):
        # Timeout ni oshirish (internet sekin bo'lsa)
        self.app = (
            Application.builder()
            .token(BOT_TOKEN)
            .connect_timeout(30.0)
            .read_timeout(30.0)
            .write_timeout(30.0)
            .build()
        )
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Handlerlarni qo'shish"""
        from bot.handlers import (
            start_command, interests_command, status_command, 
            interest_callback, help_command, stats_command, 
            latest_command, search_command,
            keywords_command, breaking_command, activate_command,
            handle_keyboard_buttons, start_trial_callback
        )
        from bot.admin_handlers import (
            admin_panel_command, channels_command, add_channel_command,
            remove_channel_command, plans_command, set_price_command,
            users_command, add_plan_command, edit_plan_command, remove_plan_command,
            delete_user_command, delete_user_callback,
            languages_command, add_language_command, remove_language_command
        )
        from bot.language_handler import language_command, language_callback
        
        # Oddiy buyruqlar
        self.app.add_handler(CommandHandler("start", start_command))
        self.app.add_handler(CommandHandler("interests", interests_command))
        self.app.add_handler(CommandHandler("status", status_command))
        self.app.add_handler(CommandHandler("help", help_command))
        self.app.add_handler(CommandHandler("stats", stats_command))
        # self.app.add_handler(CommandHandler("latest", latest_command))  # O'chirildi
        self.app.add_handler(CommandHandler("search", search_command))
        # self.app.add_handler(CommandHandler("settings", settings_command))  # O'chirildi
        # self.app.add_handler(CommandHandler("keywords", keywords_command))  # O'chirildi
        # self.app.add_handler(CommandHandler("breaking", breaking_command))  # O'chirildi
        self.app.add_handler(CommandHandler("activate", activate_command))  # Admin uchun
        self.app.add_handler(CommandHandler("language", language_command))  # Til tanlash
        
        # Admin buyruqlar
        self.app.add_handler(CommandHandler("admin", admin_panel_command))
        self.app.add_handler(CommandHandler("channels", channels_command))
        self.app.add_handler(CommandHandler("add_channel", add_channel_command))
        self.app.add_handler(CommandHandler("remove_channel", remove_channel_command))
        self.app.add_handler(CommandHandler("plans", plans_command))
        self.app.add_handler(CommandHandler("set_price", set_price_command))
        self.app.add_handler(CommandHandler("add_plan", add_plan_command))
        self.app.add_handler(CommandHandler("edit_plan", edit_plan_command))
        self.app.add_handler(CommandHandler("remove_plan", remove_plan_command))
        self.app.add_handler(CommandHandler("users", users_command))
        self.app.add_handler(CommandHandler("delete_user", delete_user_command))
        self.app.add_handler(CommandHandler("languages", languages_command))
        self.app.add_handler(CommandHandler("add_language", add_language_command))
        self.app.add_handler(CommandHandler("remove_language", remove_language_command))
        
        # Callback va message handlers
        self.app.add_handler(CallbackQueryHandler(language_callback, pattern="^(set_lang_|first_lang_)"))
        self.app.add_handler(CallbackQueryHandler(delete_user_callback, pattern="^(delete_user_|confirm_delete_|cancel_delete_)"))
        self.app.add_handler(CallbackQueryHandler(start_trial_callback, pattern="^start_trial$"))
        self.app.add_handler(CallbackQueryHandler(interest_callback))
        
        # Reply keyboard tugmalari uchun handler
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            handle_keyboard_buttons
        ))
    
    async def send_news_to_user(self, telegram_id: int, news_text: str, category: str, channel: str, media=None, forward_info=None):
        """Userga yangilik yuborish (media bilan yoki forward qilib, to'liq formatda, ko'p tillilik bilan)"""
        # User tilini olish
        from db.database import async_session
        from db.models import User
        from sqlalchemy import select
        
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            user_lang = user.language if user else 'uz'
        
        # Kategoriya nomini tarjima qilish
        from utils.translations import get_category_name
        category_name = get_category_name(category, user_lang)
        
        # Yangilik matnini tarjima qilish
        from services.translator import translate_text
        try:
            print(f"   🔄 Tarjima qilinmoqda: {user_lang} tiliga...")
            translated_news = await translate_text(news_text, user_lang)
            print(f"   ✅ Tarjima tugadi: {len(translated_news)} belgi")
        except Exception as e:
            print(f"⚠️ Yangilik tarjimasi xatosi: {e}")
            import traceback
            traceback.print_exc()
            translated_news = news_text  # Xato bo'lsa asl matnni ishlatish
        
        # Oxirgi qatorni tarjima qilish
        if user_lang == 'uz':
            footer = "📰 Boshqa kategoriyalar uchun /interests"
        elif user_lang == 'uz_cyrl':
            footer = "📰 Бошқа категориялар учун /interests"
        elif user_lang == 'ru':
            footer = "📰 Другие категории /interests"
        else:  # en
            footer = "📰 Other categories /interests"
        
        # PRODUCTION-SAFE: Build message with proper HTML escaping
        from utils.telegram_formatter import build_news_message
        caption = build_news_message(
            category_name=category_name,
            news_content=translated_news,
            footer=footer,
            escape_content=True  # CRITICAL: Escape external content
        )
        
        # Telegram caption limiti: 1024 belgi (media bilan)
        # Telegram message limiti: 4096 belgi (text only)
        
        sent_message = None
        try:
            # Agar forward_info bo'lsa - katta video, to'g'ridan-to'g'ri forward qilish
            if forward_info:
                # Avval caption yuborish (kategoriya bilan)
                from utils.telegram_formatter import send_safe_message
                await send_safe_message(
                    bot=self.app.bot,
                    chat_id=telegram_id,
                    text=category_name,
                    parse_mode="HTML"
                )
                
                # Keyin videoni forward qilish
                sent_message = await self.app.bot.forward_message(
                    chat_id=telegram_id,
                    from_chat_id=forward_info['channel'],
                    message_id=forward_info['message_id']
                )
                
                print(f"   ✅ Video forward qilindi: {telegram_id}")
                
            # Agar media bo'lsa - photo/video bilan yuborish
            elif media:
                # Media file_id yoki file object bo'lishi mumkin
                media_source = media.get('file_id') or media.get('file')
                
                # Caption limiti: 1024 belgi
                if len(caption) <= 1024:
                    if media['type'] == 'photo':
                        sent_message = await self.app.bot.send_photo(
                            chat_id=telegram_id,
                            photo=media_source,
                            caption=caption,
                            parse_mode="HTML"  # SAFE: Using HTML
                        )
                    elif media['type'] == 'video':
                        sent_message = await self.app.bot.send_video(
                            chat_id=telegram_id,
                            video=media_source,
                            caption=caption,
                            parse_mode="HTML"  # SAFE: Using HTML
                        )
                else:
                    # Caption juda uzun - media va text alohida yuborish
                    if media['type'] == 'photo':
                        sent_message = await self.app.bot.send_photo(
                            chat_id=telegram_id,
                            photo=media_source
                        )
                    elif media['type'] == 'video':
                        sent_message = await self.app.bot.send_video(
                            chat_id=telegram_id,
                            video=media_source
                        )
                    
                    # To'liq text alohida yuborish (SAFE)
                    await self._send_long_message(telegram_id, caption)
            else:
                # Faqat text - uzun bo'lsa bo'laklarga ajratish (SAFE)
                await self._send_long_message(telegram_id, caption)
                
        except Exception as e:
            import telegram
            if isinstance(e, telegram.error.Forbidden):
                print(f"❌ User {telegram_id} botni block qilgan")
            elif isinstance(e, telegram.error.BadRequest):
                print(f"❌ Noto'g'ri so'rov ({telegram_id}): {e}")
            else:
                print(f"❌ Xatolik ({telegram_id}): {e}")
        
        return sent_message  # Yuborilgan xabarni qaytarish
    
    async def _send_long_message(self, telegram_id: int, text: str):
        """
        Uzun xabarni bo'laklarga ajratib yuborish (4096 belgi limiti)
        PRODUCTION-SAFE: Uses HTML with automatic fallback
        """
        from utils.telegram_formatter import send_safe_message
        
        MAX_LENGTH = 4096
        
        if len(text) <= MAX_LENGTH:
            # Qisqa xabar - bir martada yuborish (SAFE)
            await send_safe_message(
                bot=self.app.bot,
                chat_id=telegram_id,
                text=text,
                parse_mode="HTML",  # SAFE: Using HTML
                fallback_to_plain=True  # CRITICAL: Auto-fallback
            )
        else:
            # Uzun xabar - bo'laklarga ajratish
            parts = []
            current_part = ""
            
            # Paragraflar bo'yicha ajratish
            paragraphs = text.split('\n')
            
            for para in paragraphs:
                if len(current_part) + len(para) + 1 <= MAX_LENGTH:
                    current_part += para + '\n'
                else:
                    if current_part:
                        parts.append(current_part.strip())
                    current_part = para + '\n'
            
            if current_part:
                parts.append(current_part.strip())
            
            # Har bir qismni yuborish (SAFE)
            for i, part in enumerate(parts):
                if i == 0:
                    # Birinchi qism
                    await send_safe_message(
                        bot=self.app.bot,
                        chat_id=telegram_id,
                        text=part,
                        parse_mode="HTML",
                        fallback_to_plain=True
                    )
                else:
                    # Davomi
                    from utils.telegram_formatter import format_italic
                    continuation_text = f"{format_italic('(davomi)', escape=False)}\n\n{part}"
                    
                    await send_safe_message(
                        bot=self.app.bot,
                        chat_id=telegram_id,
                        text=continuation_text,
                        parse_mode="HTML",
                        fallback_to_plain=True
                    )
                
                # Spam oldini olish uchun kichik pauza
                import asyncio
                await asyncio.sleep(0.5)
    
    async def start(self):
        """Botni ishga tushirish"""
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling(drop_pending_updates=True)
        print("✅ Bot ishga tushdi")
        
        # Polling davom etishi uchun kutish
        import asyncio
        try:
            await asyncio.Event().wait()
        except (KeyboardInterrupt, SystemExit):
            pass
    
    async def stop(self):
        """Botni to'xtatish"""
        try:
            if self.app.updater and self.app.updater.running:
                await self.app.updater.stop()
            if self.app:
                await self.app.stop()
                await self.app.shutdown()
        except Exception as e:
            print(f"⚠️ Bot to'xtatishda xato: {e}")

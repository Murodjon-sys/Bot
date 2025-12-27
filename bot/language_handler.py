"""
Til tanlash va boshqarish
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy import select
from db.models import User
from db.database import async_session
from utils.translations import LANGUAGES, get_text

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /language - Tilni o'zgartirish (dinamik, LANGUAGES dan)
    """
    telegram_id = update.effective_user.id
    
    # Hozirgi tilni olish
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        current_lang = user.language if user else 'uz'
    
    # Dinamik keyboard yaratish (LANGUAGES dan)
    # 2x2 format uchun
    keyboard = []
    lang_items = list(LANGUAGES.items())
    
    # 2 tadan qilib qatorlarga ajratish
    for i in range(0, len(lang_items), 2):
        row = []
        for j in range(2):
            if i + j < len(lang_items):
                lang_code, lang_name = lang_items[i + j]
                row.append(InlineKeyboardButton(lang_name, callback_data=f"set_lang_{lang_code}"))
        keyboard.append(row)
    
    text = get_text('select_language', current_lang)
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Til tanlash callback
    """
    query = update.callback_query
    await query.answer()
    
    data = query.data
    telegram_id = update.effective_user.id
    username = update.effective_user.username
    
    if data.startswith("first_lang_"):
        # Birinchi marta til tanlash (yangi user)
        lang_code = data.replace("first_lang_", "")
        
        from datetime import datetime, timedelta
        from config import TRIAL_DAYS, SUBSCRIPTION_PLANS
        
        # Userni yaratish (hali trial yo'q, faqat til)
        async with async_session() as session:
            user = User(
                telegram_id=telegram_id,
                username=username,
                language=lang_code
            )
            session.add(user)
            await session.commit()
        
        # Ta'riflarni ko'rsatish (tanlangan tilda)
        from utils.translations import get_text
        
        # Ta'riflar matni
        if lang_code == 'uz':
            plans_text = (
                "💰 **TARIFLAR**\n\n"
                "Quyidagi tariflardan birini tanlang:\n\n"
            )
            for plan_key, plan_info in SUBSCRIPTION_PLANS.items():
                limit_text = "Cheksiz" if plan_info.get('category_limit') is None else f"{plan_info['category_limit']} ta"
                plans_text += (
                    f"{plan_info['emoji']} **{plan_info['name']}**\n"
                    f"   💰 Narx: {plan_info['price']:,} so'm/oy\n"
                    f"   📰 Kategoriyalar: {limit_text}\n"
                    f"   ⏰ Muddat: {plan_info['duration_days']} kun\n\n"
                )
            plans_text += (
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🎁 **Bepul sinov:** {TRIAL_DAYS} kun\n"
                f"📰 Barcha kategoriyalar\n\n"
                "Boshlash tugmasini bosing!"
            )
        elif lang_code == 'uz_cyrl':
            plans_text = (
                "💰 **ТАРИФЛАР**\n\n"
                "Қуйидаги тарифлардан бирини танланг:\n\n"
            )
            for plan_key, plan_info in SUBSCRIPTION_PLANS.items():
                limit_text = "Чексиз" if plan_info.get('category_limit') is None else f"{plan_info['category_limit']} та"
                plans_text += (
                    f"{plan_info['emoji']} **{plan_info['name']}**\n"
                    f"   💰 Нарх: {plan_info['price']:,} сўм/ой\n"
                    f"   📰 Категориялар: {limit_text}\n"
                    f"   ⏰ Муддат: {plan_info['duration_days']} кун\n\n"
                )
            plans_text += (
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🎁 **Бепул синов:** {TRIAL_DAYS} кун\n"
                f"📰 Барча категориялар\n\n"
                "Бошлаш тугмасини босинг!"
            )
        elif lang_code == 'ru':
            plans_text = (
                "💰 **ТАРИФЫ**\n\n"
                "Выберите один из тарифов:\n\n"
            )
            for plan_key, plan_info in SUBSCRIPTION_PLANS.items():
                limit_text = "Безлимит" if plan_info.get('category_limit') is None else f"{plan_info['category_limit']} шт"
                plans_text += (
                    f"{plan_info['emoji']} **{plan_info['name']}**\n"
                    f"   💰 Цена: {plan_info['price']:,} сум/мес\n"
                    f"   📰 Категории: {limit_text}\n"
                    f"   ⏰ Срок: {plan_info['duration_days']} дней\n\n"
                )
            plans_text += (
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🎁 **Бесплатный пробный:** {TRIAL_DAYS} дней\n"
                f"📰 Все категории\n\n"
                "Нажмите кнопку Начать!"
            )
        else:  # en va boshqalar
            plans_text = (
                "💰 **PLANS**\n\n"
                "Choose one of the plans:\n\n"
            )
            for plan_key, plan_info in SUBSCRIPTION_PLANS.items():
                limit_text = "Unlimited" if plan_info.get('category_limit') is None else f"{plan_info['category_limit']} items"
                plans_text += (
                    f"{plan_info['emoji']} **{plan_info['name']}**\n"
                    f"   💰 Price: {plan_info['price']:,} sum/month\n"
                    f"   📰 Categories: {limit_text}\n"
                    f"   ⏰ Duration: {plan_info['duration_days']} days\n\n"
                )
            plans_text += (
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🎁 **Free trial:** {TRIAL_DAYS} days\n"
                f"📰 All categories\n\n"
                "Click Start button!"
            )
        
        # "Boshlash" tugmasi
        if lang_code == 'uz':
            start_btn_text = "🚀 Boshlash"
        elif lang_code == 'uz_cyrl':
            start_btn_text = "🚀 Бошлаш"
        elif lang_code == 'ru':
            start_btn_text = "🚀 Начать"
        else:
            start_btn_text = "🚀 Start"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(start_btn_text, callback_data="start_trial")]
        ])
        
        try:
            await query.edit_message_text(plans_text, parse_mode='Markdown', reply_markup=keyboard)
        except:
            pass
        
        return
    
    # Tilni o'zgartirish (eski user)
    if data.startswith("set_lang_"):
        lang_code = data.replace("set_lang_", "")
        
        # Tilni saqlash
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                user.language = lang_code
                await session.commit()
                
                # Tasdiqlash xabari (dinamik, har qanday til uchun)
                lang_name = LANGUAGES.get(lang_code, lang_code)
                
                # Har bir tilda alohida xabar
                if lang_code == 'uz':
                    text = (
                        f"✅ **Til o'zgartirildi!**\n\n"
                        f"Siz **{lang_name}** tilini tanladingiz.\n\n"
                        f"Endi barcha xabarlar va yangiliklar o'zbek tilida (lotin) bo'ladi."
                    )
                elif lang_code == 'uz_cyrl':
                    text = (
                        f"✅ **Тил ўзгартирилди!**\n\n"
                        f"Сиз **{lang_name}** тилини танладингиз.\n\n"
                        f"Энди барча хабарлар ва янгиликлар ўзбек тилида (кирилл) бўлади."
                    )
                elif lang_code == 'ru':
                    text = (
                        f"✅ **Язык изменен!**\n\n"
                        f"Вы выбрали **{lang_name}** язык.\n\n"
                        f"Теперь все сообщения и новости будут на русском языке."
                    )
                elif lang_code == 'en':
                    text = (
                        f"✅ **Language changed!**\n\n"
                        f"You selected **{lang_name}** language.\n\n"
                        f"Now all messages and news will be in English."
                    )
                else:
                    # Yangi tillar uchun umumiy xabar (ingliz tilida)
                    text = (
                        f"✅ **Language changed!**\n\n"
                        f"You selected **{lang_name}** language.\n\n"
                        f"Now all messages and news will be in this language."
                    )
                
                # Xabarni tahrirlash va reply keyboard qo'shish
                from bot.handlers import get_main_keyboard
                from config import ADMIN_USERNAME
                
                is_admin = (username == ADMIN_USERNAME)
                
                try:
                    # Inline xabarni tahrirlash (reply_markup ni olib tashlash)
                    await query.edit_message_text(text, parse_mode='Markdown')
                    
                    # Reply keyboard ni alohida yuborish (zero-width space - ko'rinmas)
                    await query.message.reply_text(
                        "\u200B",  # Zero-width space (invisible)
                        reply_markup=get_main_keyboard(is_admin, lang_code)
                    )
                except:
                    pass
    
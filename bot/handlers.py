from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from sqlalchemy import select
from db.models import User, UserInterest
from db.database import async_session
from config import CATEGORIES, TRIAL_DAYS, ADMIN_USERNAME, SUBSCRIPTION_PLANS
from datetime import datetime, timedelta
from utils.translations import LANGUAGES

def get_main_keyboard(is_admin=False, lang='uz'):
    """Asosiy reply keyboard - telefon va noutbuk uchun optimallashtirilgan"""
    from utils.translations import get_text
    from utils.i18n import t
    
    if is_admin:
        keyboard = [
            [KeyboardButton(get_text('btn_interests', lang)), KeyboardButton(get_text('btn_status', lang))],
            [KeyboardButton(t('btn_plans', lang)), KeyboardButton(t('btn_statistics', lang))],
            [KeyboardButton(t('btn_admin_panel', lang)), KeyboardButton(get_text('btn_help', lang))],
            [KeyboardButton(get_text('btn_language', lang))]
        ]
    else:
        keyboard = [
            [KeyboardButton(get_text('btn_interests', lang)), KeyboardButton(get_text('btn_status', lang))],
            [KeyboardButton(t('btn_plans', lang)), KeyboardButton(get_text('btn_help', lang))],
            [KeyboardButton(get_text('btn_language', lang))]
        ]
    
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Buyruqni tanlang..."
    )

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start - Botni boshlash (til tanlash bilan)
    """
    telegram_id = update.effective_user.id
    username = update.effective_user.username
    
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Yangi user - avval til tanlash (dinamik, LANGUAGES dan)
            # 2x2 format uchun
            keyboard = []
            lang_items = list(LANGUAGES.items())
            
            # 2 tadan qilib qatorlarga ajratish
            for i in range(0, len(lang_items), 2):
                row = []
                for j in range(2):
                    if i + j < len(lang_items):
                        lang_code, lang_name = lang_items[i + j]
                        row.append(InlineKeyboardButton(lang_name, callback_data=f"first_lang_{lang_code}"))
                keyboard.append(row)
            
            await update.message.reply_text(
                "🌐 Tilni tanlang\n🌐 Тилни танланг\n🌐 Выберите язык\n🌐 Select language",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            # Eski user - lekin kategoriya tanlamagan bo'lsa, yangi user kabi ko'rsatish
            from utils.translations import get_text
            
            username = update.effective_user.username
            is_admin = (username == ADMIN_USERNAME)
            
            # Til tekshiruvi - agar None bo'lsa, default 'uz' qo'yish
            lang = user.language if user.language else 'uz'
            
            # Agar til None bo'lsa, database ga saqlash
            if not user.language:
                user.language = 'uz'
                await session.commit()
            
            # Kategoriya tanlanganligini tekshirish
            result = await session.execute(
                select(UserInterest).where(UserInterest.user_id == user.id)
            )
            interests = result.scalars().all()
            
            # Agar kategoriya tanlamagan bo'lsa - yangi user kabi xabar
            if not interests:
                safe_name = update.effective_user.first_name.replace('*', '').replace('_', '').replace('[', '').replace(']', '')
                
                # Tariflar ro'yxatini dinamik yaratish
                plans_text = ""
                for plan_key, plan_info in SUBSCRIPTION_PLANS.items():
                    plans_text += f"{plan_info['emoji']} {plan_info['name']} — {plan_info['price']:,} so'm/oy\n"
                
                welcome_text = get_text('welcome', lang)
                
                inline_keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        get_text('btn_interests', lang).replace('📋 ', ''),
                        callback_data="onboarding_start"
                    )]
                ])
                
                # Reply keyboard yuborish
                await update.message.reply_text(
                    welcome_text,
                    reply_markup=get_main_keyboard(is_admin, lang),
                    parse_mode='Markdown'
                )
                
                # Inline keyboard alohida yuborish
                await update.message.reply_text(
                    get_text('select_interests', lang),
                    reply_markup=inline_keyboard
                )
            else:
                # Kategoriya tanlagan - oddiy xabar
                safe_name = update.effective_user.first_name.replace('*', '').replace('_', '').replace('[', '').replace(']', '')
                
                welcome_back = get_text('welcome', lang)
                await update.message.reply_text(
                    welcome_back, 
                    reply_markup=get_main_keyboard(is_admin, lang), 
                    parse_mode='Markdown'
                )

async def get_interests_keyboard(telegram_id=None, lang='uz'):
    """Qiziqishlar uchun keyboard (ko'p tillilik bilan)"""
    from utils.translations import get_category_name
    
    category_icons = {
        'siyosat': '🏛',
        'iqtisod': '💰',
        'jamiyat': '👥',
        'sport': '⚽',
        'texnologiya': '💻',
        'dunyo': '🌍',
        'salomatlik': '🩺',
        'obhavo': '🌤'
    }
    
    selected_categories = set()
    if telegram_id:
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                result = await session.execute(
                    select(UserInterest).where(UserInterest.user_id == user.id)
                )
                interests = result.scalars().all()
                selected_categories = {i.category for i in interests}
    
    keyboard = []
    categories = list(CATEGORIES.keys())
    
    for i in range(0, len(categories), 2):
        row = []
        for j in range(i, min(i + 2, len(categories))):
            category = categories[j]
            icon = category_icons.get(category, '📌')
            label = get_category_name(category, lang)
            
            row.append(InlineKeyboardButton(
                label,
                callback_data=f"show_news_{category}"
            ))
        keyboard.append(row)
    
    return InlineKeyboardMarkup(keyboard)


async def start_trial_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Boshlash tugmasi bosilganda - trial ni aktivlashtirish"""
    query = update.callback_query
    await query.answer()
    
    telegram_id = update.effective_user.id
    username = update.effective_user.username
    
    from datetime import datetime, timedelta
    from config import TRIAL_DAYS, ADMIN_USERNAME
    from utils.translations import get_text
    
    # Trial ni aktivlashtirish
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.trial_end = datetime.utcnow() + timedelta(days=TRIAL_DAYS)
            await session.commit()
            
            lang_code = user.language
            
            # Welcome xabar (tanlangan tilda)
            if lang_code == 'uz':
                welcome_text = (
                    "🎉 Xush kelibsiz!\n\n"
                    f"Sizga {TRIAL_DAYS} kunlik bepul sinov berildi!\n\n"
                    "📱 Endi qiziqishlaringizni tanlang va yangiliklarni oling!"
                )
            elif lang_code == 'uz_cyrl':
                welcome_text = (
                    "🎉 Хуш келибсиз!\n\n"
                    f"Сизга {TRIAL_DAYS} кунлик бепул синов берилди!\n\n"
                    "📱 Энди қизиқишларингизни танланг ва янгиликларни олинг!"
                )
            elif lang_code == 'ru':
                welcome_text = (
                    "🎉 Добро пожаловать!\n\n"
                    f"Вам предоставлен бесплатный пробный период на {TRIAL_DAYS} дней!\n\n"
                    "📱 Теперь выберите свои интересы и получайте новости!"
                )
            else:  # en
                welcome_text = (
                    "🎉 Welcome!\n\n"
                    f"You have been given a {TRIAL_DAYS}-day free trial!\n\n"
                    "📱 Now choose your interests and get news!"
                )
            
            # Reply keyboard yuborish (AVVAL)
            is_admin = (username == ADMIN_USERNAME)
            
            # Birinchi xabar - reply keyboard bilan
            await query.message.reply_text(
                welcome_text,
                reply_markup=get_main_keyboard(is_admin, lang_code)
            )
            
            # Inline xabarni o'chirish
            try:
                await query.edit_message_text("✅")
            except:
                pass
            
            # Qiziqishlar tanlash inline keyboard
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            inline_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    get_text('btn_interests', lang_code).replace('📋 ', '') + ' →',
                    callback_data="onboarding_start"
                )]
            ])
            
            await query.message.reply_text(
                get_text('select_interests', lang_code),
                reply_markup=inline_keyboard
            )


async def interest_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kategoriya tanlanganda"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "show_plans":
        # User tilini olish
        telegram_id = update.effective_user.id
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            lang = user.language if user else 'uz'
        
        from utils.i18n import t
        
        text = f"{t('subscription_plans_header', lang)}\n\n"
        text += "━━━━━━━━━━━━━━━━━━━━\n\n"
        text += f"{t('which_plan', lang)}\n\n"
        
        keyboard = []
        for plan_key, plan_info in SUBSCRIPTION_PLANS.items():
            # Kategoriya limiti
            if plan_info.get('category_limit'):
                limit_text = t('plan_categories', lang, limit=f"{plan_info['category_limit']}")
            else:
                limit_text = t('plan_categories', lang, limit=t('unlimited', lang))
            
            text += (
                f"{plan_info['emoji']} **{plan_info['name']}**\n"
                f"   {t('plan_price', lang, price=plan_info['price'])}\n"
                f"   {limit_text}\n"
                f"   {t('plan_duration', lang, days=plan_info['duration_days'])}\n\n"
            )
            keyboard.append([
                InlineKeyboardButton(
                    f"{plan_info['emoji']} {plan_info['name']} — {plan_info['price']:,}",
                    callback_data=f"select_plan_{plan_key}"
                )
            ])
        
        text += "━━━━━━━━━━━━━━━━━━━━\n\n"
        text += "👇 Tarifni tanlang:"
        
        try:
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        except:
            pass
        return
    
    if data.startswith("select_plan_"):
        plan_key = data.replace("select_plan_", "")
        plan_info = SUBSCRIPTION_PLANS.get(plan_key)
        
        if not plan_info:
            await query.answer("❌ Noto'g'ri tarif")
            return
        
        text = (
            f"{plan_info['emoji']} **{plan_info['name'].upper()} TARIF**\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💰 **Narx:** {plan_info['price']:,} so'm\n"
            f"⏰ **Muddat:** {plan_info['duration_days']} kun\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📱 **To'lov uchun:**\n\n"
            f"1️⃣ Click yoki Payme orqali to'lang\n"
            f"2️⃣ Chekni adminga yuboring: @Murodjon_PM\n"
            f"3️⃣ Obuna faollashtiriladi!\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💡 **Karta raqami:**\n"
            f"`8600 1234 5678 9012`\n\n"
            f"_(Murodjon Latipov)_"
        )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ To'lov qildim", callback_data=f"paid_{plan_key}")],
            [InlineKeyboardButton("◀️ Orqaga", callback_data="show_plans")]
        ])
        
        try:
            await query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        except:
            pass
        return
    
    if data.startswith("paid_"):
        plan_key = data.replace("paid_", "")
        plan_info = SUBSCRIPTION_PLANS.get(plan_key)
        
        text = (
            "✅ **RAHMAT!**\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "To'lovingiz qabul qilindi.\n\n"
            "Admin tekshirgach obunangiz faollashtiriladi.\n\n"
            "⏰ Odatda 5-10 daqiqa ichida.\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📞 Savol bo'lsa: @Murodjon_PM"
        )
        
        try:
            await query.edit_message_text(text, parse_mode='Markdown')
        except:
            pass
        return
    
    if data == "onboarding_start":
        telegram_id = update.effective_user.id
        
        # User tilini olish
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            lang = user.language if user else 'uz'
        
        # Xabarni tarjima qilish
        if lang == 'uz':
            text = (
                "📰 **YANGILIKLAR**\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "Qaysi kategoriya bo'yicha yangiliklar kerak?\n\n"
                "👇 Kategoriyani tanlang:"
            )
        elif lang == 'uz_cyrl':
            text = (
                "📰 **ЯНГИЛИКЛАР**\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "Қайси категория бўйича янгиликлар керак?\n\n"
                "👇 Категорияни танланг:"
            )
        elif lang == 'ru':
            text = (
                "📰 **НОВОСТИ**\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "По какой категории нужны новости?\n\n"
                "👇 Выберите категорию:"
            )
        else:  # en
            text = (
                "📰 **NEWS**\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "Which category do you want news from?\n\n"
                "👇 Choose a category:"
            )
        
        keyboard = await get_interests_keyboard(telegram_id, lang)
        
        try:
            await query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        except:
            pass
        return
    
    if data.startswith("show_news_"):
        category = data.replace("show_news_", "")
        telegram_id = update.effective_user.id
        
        category_emojis = {
            'siyosat': '🏛',
            'iqtisod': '💰',
            'jamiyat': '👥',
            'sport': '⚽',
            'texnologiya': '💻',
            'dunyo': '🌍',
            'salomatlik': '🏥',
            'obhavo': '🌤'
        }
        emoji = category_emojis.get(category, '📌')
        
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                result = await session.execute(
                    select(UserInterest).where(
                        UserInterest.user_id == user.id,
                        UserInterest.category == category
                    )
                )
                interest = result.scalar_one_or_none()
                
                if interest:
                    from db.models import News
                    result = await session.execute(
                        select(News)
                        .where(News.category == category)
                        .order_by(News.created_at.desc())
                        .limit(1)
                    )
                    latest_news = result.scalar_one_or_none()
                    
                    if latest_news:
                        # Agar media bo'lsa - rasm/video bilan yuborish
                        # 1. Agar media_file_id bo'lsa - file_id orqali yuborish
                        # 2. Agar media_file_id yo'q lekin channel_username va channel_message_id bo'lsa - forward qilish
                        if latest_news.media_file_id and latest_news.media_type:
                            try:
                                await query.edit_message_text(
                                    f"{emoji} **{category.upper()}**\n\n"
                                    f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                    f"Bu kategoriya allaqachon tanlangan.\n\n"
                                    f"📰 Eng oxirgi yangilik:",
                                    parse_mode='Markdown'
                                )
                                
                                # User tilini olish va yangilik matnini tarjima qilish
                                lang = user.language
                                from services.translator import translate_text
                                from utils.translations import get_category_name
                                from utils.i18n import t
                                
                                try:
                                    translated_text = await translate_text(latest_news.text, lang)
                                except Exception as e:
                                    print(f"⚠️ Tarjima xatosi: {e}")
                                    translated_text = latest_news.text
                                
                                # Kategoriya nomini tarjima qilish
                                category_name = get_category_name(category, lang)
                                footer = t('other_categories', lang)
                                
                                # Context orqali bot instance olish
                                bot_instance = context.bot
                                if bot_instance:
                                    caption = f"{category_name}\n\n{translated_text}\n\n━━━━━━━━━━━━━━━━━━━━\n\n{footer}"
                                    
                                    if latest_news.media_type == 'photo':
                                        await bot_instance.send_photo(
                                            chat_id=telegram_id,
                                            photo=latest_news.media_file_id,
                                            caption=caption,
                                            parse_mode='Markdown'
                                        )
                                    elif latest_news.media_type == 'video':
                                        await bot_instance.send_video(
                                            chat_id=telegram_id,
                                            video=latest_news.media_file_id,
                                            caption=caption,
                                            parse_mode='Markdown'
                                        )
                                return
                            except Exception as e:
                                print(f"❌ Media yuborishda xato: {e}")
                                import traceback
                                traceback.print_exc()
                        elif latest_news.media_type and latest_news.channel_username and latest_news.channel_message_id:
                            # Agar media_file_id yo'q lekin kanal ma'lumotlari bo'lsa - forward qilish
                            try:
                                # User tilini olish
                                lang = user.language
                                from services.translator import translate_text
                                from utils.translations import get_category_name
                                from utils.i18n import t
                                
                                # Kategoriya nomini tarjima qilish
                                category_name = get_category_name(category, lang)
                                
                                # Header xabari (tanlangan tilda)
                                if lang == 'uz':
                                    header_msg = f"{category_name}\n\n━━━━━━━━━━━━━━━━━━━━\n\nBu kategoriya allaqachon tanlangan.\n\n📰 Eng oxirgi yangilik:"
                                elif lang == 'uz_cyrl':
                                    header_msg = f"{category_name}\n\n━━━━━━━━━━━━━━━━━━━━\n\nБу категория аллақачон танланган.\n\n📰 Энг охирги янгилик:"
                                elif lang == 'ru':
                                    header_msg = f"{category_name}\n\n━━━━━━━━━━━━━━━━━━━━\n\nЭта категория уже выбрана.\n\n📰 Последняя новость:"
                                else:  # en
                                    header_msg = f"{category_name}\n\n━━━━━━━━━━━━━━━━━━━━\n\nThis category is already selected.\n\n📰 Latest news:"
                                
                                await query.edit_message_text(
                                    header_msg,
                                    parse_mode='Markdown'
                                )
                                
                                # Telethon orqali forward qilish
                                from listener.channel_listener import get_telethon_client
                                client = await get_telethon_client()
                                if client:
                                    try:
                                        # Kanaldan xabarni forward qilish
                                        await client.forward_messages(
                                            entity=telegram_id,
                                            messages=latest_news.channel_message_id,
                                            from_peer=latest_news.channel_username
                                        )
                                        
                                        # Yangilik matnini tarjima qilish
                                        try:
                                            translated_text = await translate_text(latest_news.text, lang)
                                        except Exception as e:
                                            print(f"⚠️ Tarjima xatosi: {e}")
                                            translated_text = latest_news.text
                                        
                                        footer = t('other_categories', lang)
                                        
                                        # Caption yuborish (tarjima qilingan)
                                        bot_instance = context.bot
                                        if bot_instance:
                                            caption = f"{category_name}\n\n{translated_text}\n\n━━━━━━━━━━━━━━━━━━━━\n\n{footer}"
                                            await bot_instance.send_message(
                                                chat_id=telegram_id,
                                                text=caption,
                                                parse_mode='Markdown'
                                            )
                                        return
                                    except Exception as e:
                                        print(f"❌ Forward qilishda xato: {e}")
                                        import traceback
                                        traceback.print_exc()
                            except Exception as e:
                                print(f"❌ Telethon client olishda xato: {e}")
                                import traceback
                                traceback.print_exc()
                        
                        # Agar media yo'q bo'lsa - faqat matn (tarjima bilan)
                        # User tilini olish
                        lang = user.language
                        
                        # Yangilik matnini tarjima qilish
                        from services.translator import translate_text
                        from utils.translations import get_category_name
                        from utils.i18n import t
                        
                        try:
                            translated_text = await translate_text(latest_news.text, lang)
                        except Exception as e:
                            print(f"⚠️ Tarjima xatosi: {e}")
                            translated_text = latest_news.text
                        
                        # Kategoriya nomini tarjima qilish
                        category_name = get_category_name(category, lang)
                        footer = t('other_categories', lang)
                        
                        # Xabar yaratish (tanlangan tilda)
                        if lang == 'uz':
                            message = (
                                f"{category_name}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"Bu kategoriya allaqachon tanlangan.\n\n"
                                f"📰 Eng oxirgi yangilik:\n\n"
                                f"{translated_text}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"{footer}"
                            )
                        elif lang == 'uz_cyrl':
                            message = (
                                f"{category_name}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"Бу категория аллақачон танланган.\n\n"
                                f"📰 Энг охирги янгилик:\n\n"
                                f"{translated_text}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"{footer}"
                            )
                        elif lang == 'ru':
                            message = (
                                f"{category_name}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"Эта категория уже выбрана.\n\n"
                                f"📰 Последняя новость:\n\n"
                                f"{translated_text}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"{footer}"
                            )
                        else:  # en
                            message = (
                                f"{category_name}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"This category is already selected.\n\n"
                                f"📰 Latest news:\n\n"
                                f"{translated_text}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"{footer}"
                            )
                    else:
                        # Yangilik yo'q (tarjima bilan)
                        lang = user.language
                        from utils.translations import get_category_name
                        from utils.i18n import t
                        
                        category_name = get_category_name(category, lang)
                        footer = t('other_categories', lang)
                        
                        if lang == 'uz':
                            message = (
                                f"{category_name}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"Bu kategoriya allaqachon tanlangan.\n\n"
                                f"Hozircha bu kategoriyada yangiliklar yo'q.\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"{footer}"
                            )
                        elif lang == 'uz_cyrl':
                            message = (
                                f"{category_name}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"Бу категория аллақачон танланган.\n\n"
                                f"Ҳозирча бу категорияда янгиликлар йўқ.\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"{footer}"
                            )
                        elif lang == 'ru':
                            message = (
                                f"{category_name}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"Эта категория уже выбрана.\n\n"
                                f"Пока в этой категории нет новостей.\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"{footer}"
                            )
                        else:  # en
                            message = (
                                f"{category_name}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"This category is already selected.\n\n"
                                f"No news in this category yet.\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"{footer}"
                            )
                else:
                    # Yangi kategoriya qo'shishdan oldin limit tekshirish
                    # Admin uchun limit yo'q
                    telegram_id = update.effective_user.id
                    username_check = update.effective_user.username
                    is_admin = (username_check == ADMIN_USERNAME)
                    
                    # User tilini olish
                    lang = user.language if user.language else 'uz'
                    
                    if not is_admin:
                        # Hozirgi kategoriyalar sonini olish
                        result_count = await session.execute(
                            select(UserInterest).where(UserInterest.user_id == user.id)
                        )
                        current_interests = result_count.scalars().all()
                        current_count = len(current_interests)
                        
                        # Tarif tekshirish
                        has_trial = user.trial_end and user.trial_end > datetime.utcnow()
                        has_subscription = user.subscription_end and user.subscription_end > datetime.utcnow()
                        
                        # Tarif bo'yicha limit
                        limit = None
                        tarif_name = None
                        
                        if has_subscription:
                            # Pullik tarif
                            if user.subscription_plan == 'basic':
                                limit = 3
                                tarif_name = "📦 Basic"
                            elif user.subscription_plan == 'premium':
                                limit = None  # Cheksiz
                                tarif_name = "⭐ Premium"
                        elif has_trial:
                            # Bepul trial
                            limit = 1
                            tarif_name = "🎁 Bepul"
                        
                        # Limit tekshirish
                        if limit is not None and current_count >= limit:
                            # Limit oshdi
                            from utils.translations import get_category_name
                            categories_list = "\n".join([f"• {get_category_name(i.category, lang)}" for i in current_interests])
                            
                            if tarif_name == "🎁 Bepul":
                                # Bepul tarifdan pullik tarifga o'tish taklifi
                                if lang == 'uz':
                                    message = (
                                        f"⚠️ **LIMIT**\n\n"
                                        f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                        f"Siz **bepul tarif**dasiz.\n\n"
                                        f"Bepul tarifda faqat **{limit} ta kategoriya** tanlashingiz mumkin.\n\n"
                                        f"Siz allaqachon tanlagan kategoriya:\n"
                                        f"{categories_list}\n\n"
                                        f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                        f"💡 **Ko'proq kategoriya uchun:**\n\n"
                                        f"Pullik tarifga o'ting:\n\n"
                                        f"📦 Basic — 7,000 so'm/oy (**3 ta** kategoriya)\n"
                                        f"⭐ Premium — 15,000 so'm/oy (**Cheksiz** kategoriya)"
                                    )
                                elif lang == 'uz_cyrl':
                                    message = (
                                        f"⚠️ **ЛИМИТ**\n\n"
                                        f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                        f"Сиз **бепул тариф**дасиз.\n\n"
                                        f"Бепул тарифда фақат **{limit} та категория** танлашингиз мумкин.\n\n"
                                        f"Сиз аллақачон танлаган категория:\n"
                                        f"{categories_list}\n\n"
                                        f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                        f"💡 **Кўпроқ категория учун:**\n\n"
                                        f"Пуллик тарифга ўтинг:\n\n"
                                        f"📦 Basic — 7,000 сўм/ой (**3 та** категория)\n"
                                        f"⭐ Premium — 15,000 сўм/ой (**Чексиз** категория)"
                                    )
                                elif lang == 'ru':
                                    message = (
                                        f"⚠️ **ЛИМИТ**\n\n"
                                        f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                        f"Вы на **бесплатном тарифе**.\n\n"
                                        f"На бесплатном тарифе можно выбрать только **{limit} категорию**.\n\n"
                                        f"Вы уже выбрали категорию:\n"
                                        f"{categories_list}\n\n"
                                        f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                        f"💡 **Для большего количества категорий:**\n\n"
                                        f"Перейдите на платный тариф:\n\n"
                                        f"📦 Basic — 7,000 сум/мес (**3** категории)\n"
                                        f"⭐ Premium — 15,000 сум/мес (**Безлимит** категорий)"
                                    )
                                else:  # en
                                    message = (
                                        f"⚠️ **LIMIT**\n\n"
                                        f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                        f"You are on **free trial**.\n\n"
                                        f"Free trial allows only **{limit} category**.\n\n"
                                        f"You have already selected category:\n"
                                        f"{categories_list}\n\n"
                                        f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                        f"💡 **For more categories:**\n\n"
                                        f"Upgrade to paid plan:\n\n"
                                        f"📦 Basic — 7,000 sum/month (**3** categories)\n"
                                        f"⭐ Premium — 15,000 sum/month (**Unlimited** categories)"
                                    )
                            else:
                                # Basic tarifdan Premium ga o'tish taklifi
                                if lang == 'uz':
                                    message = (
                                        f"⚠️ **LIMIT**\n\n"
                                        f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                        f"Siz {tarif_name} tarifdasiz.\n\n"
                                        f"Bu tarifda maksimal **{limit} ta kategoriya** tanlashingiz mumkin.\n\n"
                                        f"Siz allaqachon tanlagan kategoriyalar:\n"
                                        f"{categories_list}\n\n"
                                        f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                        f"💡 **Ko'proq kategoriya uchun:**\n\n"
                                        f"⭐ Premium tarifga o'ting — 15,000 so'm/oy\n"
                                        f"**Cheksiz kategoriya** tanlang!"
                                    )
                                elif lang == 'uz_cyrl':
                                    message = (
                                        f"⚠️ **ЛИМИТ**\n\n"
                                        f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                        f"Сиз {tarif_name} тарифдасиз.\n\n"
                                        f"Бу тарифда максимал **{limit} та категория** танлашингиз мумкин.\n\n"
                                        f"Сиз аллақачон танлаган категориялар:\n"
                                        f"{categories_list}\n\n"
                                        f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                        f"💡 **Кўпроқ категория учун:**\n\n"
                                        f"⭐ Premium тарифга ўтинг — 15,000 сўм/ой\n"
                                        f"**Чексиз категория** танланг!"
                                    )
                                elif lang == 'ru':
                                    message = (
                                        f"⚠️ **ЛИМИТ**\n\n"
                                        f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                        f"Вы на тарифе {tarif_name}.\n\n"
                                        f"На этом тарифе можно выбрать максимум **{limit} категории**.\n\n"
                                        f"Вы уже выбрали категории:\n"
                                        f"{categories_list}\n\n"
                                        f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                        f"💡 **Для большего количества категорий:**\n\n"
                                        f"⭐ Перейдите на Premium — 15,000 сум/мес\n"
                                        f"**Безлимит категорий**!"
                                    )
                                else:  # en
                                    message = (
                                        f"⚠️ **LIMIT**\n\n"
                                        f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                        f"You are on {tarif_name} plan.\n\n"
                                        f"This plan allows maximum **{limit} categories**.\n\n"
                                        f"You have already selected categories:\n"
                                        f"{categories_list}\n\n"
                                        f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                        f"💡 **For more categories:**\n\n"
                                        f"⭐ Upgrade to Premium — 15,000 sum/month\n"
                                        f"**Unlimited categories**!"
                                    )
                            
                            from utils.i18n import t as translate
                            keyboard = InlineKeyboardMarkup([
                                [InlineKeyboardButton(translate('btn_view_plans', lang), callback_data="show_plans")],
                                [InlineKeyboardButton(translate('btn_back', lang), callback_data="onboarding_start")]
                            ])
                            
                            try:
                                await query.edit_message_text(
                                    message,
                                    reply_markup=keyboard,
                                    parse_mode='Markdown'
                                )
                            except:
                                pass
                            return
                    
                    # Agar limit yo'q bo'lsa yoki limit oshmaganida - yangi kategoriya qo'shish
                    new_interest = UserInterest(user_id=user.id, category=category)
                    session.add(new_interest)
                    await session.commit()
                    
                    from db.models import News
                    result = await session.execute(
                        select(News)
                        .where(News.category == category)
                        .order_by(News.created_at.desc())
                        .limit(1)
                    )
                    latest_news = result.scalar_one_or_none()
                    
                    if latest_news:
                        # User tilini olish
                        lang = user.language
                        
                        # Yangilik matnini tarjima qilish
                        from services.translator import translate_text
                        from utils.translations import get_category_name
                        from utils.i18n import t
                        
                        try:
                            translated_text = await translate_text(latest_news.text, lang)
                        except Exception as e:
                            print(f"⚠️ Tarjima xatosi: {e}")
                            translated_text = latest_news.text
                        
                        # Kategoriya nomini tarjima qilish
                        category_name = get_category_name(category, lang)
                        
                        # Footer matnini tarjima qilish
                        footer = t('other_categories', lang)
                        
                        # Agar media bo'lsa - rasm/video bilan yuborish
                        if latest_news.media_file_id and latest_news.media_type:
                            try:
                                # Xabar matnini tarjima qilish
                                if lang == 'uz':
                                    header_msg = f"{category_name}\n\n━━━━━━━━━━━━━━━━━━━━\n\n✅ Muvaffaqiyatli tanlandi!\n\n📰 Eng oxirgi yangilik:"
                                elif lang == 'uz_cyrl':
                                    header_msg = f"{category_name}\n\n━━━━━━━━━━━━━━━━━━━━\n\n✅ Муваффақиятли танланди!\n\n📰 Энг охирги янгилик:"
                                elif lang == 'ru':
                                    header_msg = f"{category_name}\n\n━━━━━━━━━━━━━━━━━━━━\n\n✅ Успешно выбрано!\n\n📰 Последняя новость:"
                                else:  # en
                                    header_msg = f"{category_name}\n\n━━━━━━━━━━━━━━━━━━━━\n\n✅ Successfully selected!\n\n📰 Latest news:"
                                
                                await query.edit_message_text(
                                    header_msg,
                                    parse_mode='Markdown'
                                )
                                
                                # Context orqali bot instance olish
                                bot_instance = context.bot
                                if bot_instance:
                                    caption = f"{category_name}\n\n{translated_text}\n\n━━━━━━━━━━━━━━━━━━━━\n\n{footer}"
                                    
                                    if latest_news.media_type == 'photo':
                                        await bot_instance.send_photo(
                                            chat_id=telegram_id,
                                            photo=latest_news.media_file_id,
                                            caption=caption,
                                            parse_mode='Markdown'
                                        )
                                    elif latest_news.media_type == 'video':
                                        await bot_instance.send_video(
                                            chat_id=telegram_id,
                                            video=latest_news.media_file_id,
                                            caption=caption,
                                            parse_mode='Markdown'
                                        )
                                return
                            except Exception as e:
                                print(f"❌ Media yuborishda xato: {e}")
                                import traceback
                                traceback.print_exc()
                        
                        # Agar media yo'q bo'lsa - faqat matn
                        # Oddiy matn (media yo'q yoki xato bo'lgan)
                        if lang == 'uz':
                            message = (
                                f"{category_name}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"✅ Muvaffaqiyatli tanlandi!\n\n"
                                f"📰 Eng oxirgi yangilik:\n\n"
                                f"{translated_text}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"{footer}"
                            )
                        elif lang == 'uz_cyrl':
                            message = (
                                f"{category_name}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"✅ Муваффақиятли танланди!\n\n"
                                f"📰 Энг охирги янгилик:\n\n"
                                f"{translated_text}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"{footer}"
                            )
                        elif lang == 'ru':
                            message = (
                                f"{category_name}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"✅ Успешно выбрано!\n\n"
                                f"📰 Последняя новость:\n\n"
                                f"{translated_text}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"{footer}"
                            )
                        else:  # en
                            message = (
                                f"{category_name}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"✅ Successfully selected!\n\n"
                                f"📰 Latest news:\n\n"
                                f"{translated_text}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"{footer}"
                            )
                    else:
                        # Yangilik yo'q
                        lang = user.language
                        from utils.translations import get_category_name
                        from utils.i18n import t
                        
                        category_name = get_category_name(category, lang)
                        footer = t('other_categories', lang)
                        
                        if lang == 'uz':
                            message = (
                                f"{category_name}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"✅ Muvaffaqiyatli tanlandi!\n\n"
                                f"Hozircha bu kategoriyada yangiliklar yo'q.\n\n"
                                f"Yangiliklar kelishi bilan sizga avtomatik yuboriladi.\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"{footer}"
                            )
                        elif lang == 'uz_cyrl':
                            message = (
                                f"{category_name}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"✅ Муваффақиятли танланди!\n\n"
                                f"Ҳозирча бу категорияда янгиликлар йўқ.\n\n"
                                f"Янгиликлар келиши билан сизга автоматик юборилади.\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"{footer}"
                            )
                        elif lang == 'ru':
                            message = (
                                f"{category_name}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"✅ Успешно выбрано!\n\n"
                                f"Пока в этой категории нет новостей.\n\n"
                                f"Как только появятся новости, они будут автоматически отправлены вам.\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"{footer}"
                            )
                        else:  # en
                            message = (
                                f"{category_name}\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"✅ Successfully selected!\n\n"
                                f"No news in this category yet.\n\n"
                                f"News will be automatically sent to you as soon as they arrive.\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"{footer}"
                            )
                
                try:
                    await query.edit_message_text(
                        message,
                        parse_mode='Markdown'
                    )
                except:
                    pass
        
        return

async def interests_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Qiziqishlarni ko'rish (ko'p tillilik bilan)"""
    telegram_id = update.effective_user.id
    
    # User tilini olish
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            lang = 'uz'
        else:
            lang = user.language
    
    from utils.translations import get_text
    
    text = get_text('select_interests', lang)
    
    keyboard = await get_interests_keyboard(telegram_id, lang)
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User statusini ko'rish (zamonaviy dizayn)"""
    telegram_id = update.effective_user.id
    
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await update.message.reply_text("❌ Siz ro'yxatdan o'tmagansiz. /start ni bosing.")
            return
        
        from utils.translations import get_text, get_category_name
        lang = user.language
        
        # Status ma'lumotlari
        now = datetime.utcnow()
        
        # Tarif va qolgan kunlar
        if user.subscription_end and user.subscription_end > now:
            days_left = (user.subscription_end - now).days
            plan_info = SUBSCRIPTION_PLANS.get(user.subscription_plan, SUBSCRIPTION_PLANS['basic'])
            status_emoji = plan_info['emoji']
            plan_name = plan_info['name']
            
            if lang == 'uz':
                status_line = f"{status_emoji} **{plan_name}** obuna"
                days_line = f"⏰ {days_left} kun qoldi"
            elif lang == 'uz_cyrl':
                status_line = f"{status_emoji} **{plan_name}** обуна"
                days_line = f"⏰ {days_left} кун қолди"
            elif lang == 'ru':
                status_line = f"{status_emoji} Подписка **{plan_name}**"
                days_line = f"⏰ Осталось {days_left} дней"
            else:  # en
                status_line = f"{status_emoji} **{plan_name}** subscription"
                days_line = f"⏰ {days_left} days left"
                
            is_active = True
        elif user.trial_end and user.trial_end > now:
            days_left = (user.trial_end - now).days
            status_emoji = "🎁"
            
            if lang == 'uz':
                status_line = f"{status_emoji} **Bepul sinov**"
                days_line = f"⏰ {days_left} kun qoldi"
            elif lang == 'uz_cyrl':
                status_line = f"{status_emoji} **Бепул синов**"
                days_line = f"⏰ {days_left} кун қолди"
            elif lang == 'ru':
                status_line = f"{status_emoji} **Пробный период**"
                days_line = f"⏰ Осталось {days_left} дней"
            else:  # en
                status_line = f"{status_emoji} **Free trial**"
                days_line = f"⏰ {days_left} days left"
                
            is_active = True
        else:
            status_emoji = "⏰"
            
            if lang == 'uz':
                status_line = f"{status_emoji} **Tugagan**"
                days_line = "💳 Obuna bo'ling"
            elif lang == 'uz_cyrl':
                status_line = f"{status_emoji} **Тугаган**"
                days_line = "💳 Обуна бўлинг"
            elif lang == 'ru':
                status_line = f"{status_emoji} **Истекла**"
                days_line = "💳 Оформите подписку"
            else:  # en
                status_line = f"{status_emoji} **Expired**"
                days_line = "💳 Subscribe now"
                
            is_active = False
        
        # Qiziqishlar
        result = await session.execute(
            select(UserInterest).where(UserInterest.user_id == user.id)
        )
        interests = result.scalars().all()
        
        if interests:
            interests_list = ", ".join([get_category_name(i.category, lang).replace('🏛 ', '').replace('💰 ', '').replace('👥 ', '').replace('⚽ ', '').replace('💻 ', '').replace('🌍 ', '').replace('🏥 ', '').replace('🌤 ', '') for i in interests])
        else:
            if lang == 'uz':
                interests_list = "Tanlanmagan"
            elif lang == 'uz_cyrl':
                interests_list = "Танланмаган"
            elif lang == 'ru':
                interests_list = "Не выбрано"
            else:  # en
                interests_list = "Not selected"
        
        # Zamonaviy dizayn
        username_str = f"@{user.username}" if user.username else "—"
        lang_display = LANGUAGES.get(lang, "O'zbek")
        
        if lang == 'uz':
            profile_text = (
                f"👤 PROFIL\n\n"
                f"┌ 📱 Username: {username_str}\n"
                f"├ 🌐 Til: {lang_display}\n"
                f"├ {status_line}\n"
                f"└ {days_line}\n\n"
                f"📰 Qiziqishlar: {interests_list}"
            )
        elif lang == 'uz_cyrl':
            profile_text = (
                f"👤 ПРОФИЛ\n\n"
                f"┌ 📱 Username: {username_str}\n"
                f"├ 🌐 Тил: {lang_display}\n"
                f"├ {status_line}\n"
                f"└ {days_line}\n\n"
                f"📰 Қизиқишлар: {interests_list}"
            )
        elif lang == 'ru':
            profile_text = (
                f"👤 ПРОФИЛЬ\n\n"
                f"┌ 📱 Username: {username_str}\n"
                f"├ 🌐 Язык: {lang_display}\n"
                f"├ {status_line}\n"
                f"└ {days_line}\n\n"
                f"📰 Интересы: {interests_list}"
            )
        else:  # en
            profile_text = (
                f"👤 PROFILE\n\n"
                f"┌ 📱 Username: {username_str}\n"
                f"├ 🌐 Language: {lang_display}\n"
                f"├ {status_line}\n"
                f"└ {days_line}\n\n"
                f"📰 Interests: {interests_list}"
            )
        
        # Tugma
        keyboard = None
        if not is_active:
            if lang == 'uz':
                btn_text = "💳 Obuna bo'lish"
            elif lang == 'uz_cyrl':
                btn_text = "💳 Обуна бўлиш"
            elif lang == 'ru':
                btn_text = "💳 Подписаться"
            else:  # en
                btn_text = "💳 Subscribe"
                
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(btn_text, callback_data="show_plans")]
            ])
        
        await update.message.reply_text(profile_text, reply_markup=keyboard)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam (ko'p tillilik bilan)"""
    telegram_id = update.effective_user.id
    username = update.effective_user.username
    
    # User tilini olish
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            lang = 'uz'
        else:
            lang = user.language
    
    from utils.translations import get_text
    
    admin_commands = ""
    if username == ADMIN_USERNAME:
        admin_commands = "📊 /stats — Statistika\n"
    
    help_text = get_text('help_text', lang)
    
    await update.message.reply_text(help_text)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Statistika (faqat admin)"""
    username = update.effective_user.username
    if username != ADMIN_USERNAME:
        await update.message.reply_text(
            "❌ **Ruxsat yo'q**\n\n"
            "Bu buyruq faqat admin uchun.",
            parse_mode='Markdown'
        )
        return
    
    from db.models import News, User
    
    async with async_session() as session:
        result = await session.execute(select(News))
        total_news = len(result.scalars().all())
        
        result = await session.execute(select(User))
        total_users = len(result.scalars().all())
        
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        result = await session.execute(
            select(News).where(News.created_at >= today_start)
        )
        today_news = len(result.scalars().all())
        
        category_stats = {}
        for category in CATEGORIES.keys():
            result = await session.execute(
                select(News).where(News.category == category)
            )
            category_stats[category] = len(result.scalars().all())
    
    category_emojis = {
        'siyosat': '🏛',
        'iqtisod': '💰',
        'jamiyat': '👥',
        'sport': '⚽',
        'texnologiya': '💻',
        'dunyo': '🌍',
        'salomatlik': '🩺',
        'obhavo': '🌤'
    }
    
    stats_text = (
        "📊 **STATISTIKA**\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📰 Jami yangiliklar: **{total_news}**\n"
        f"👥 Foydalanuvchilar: **{total_users}**\n"
        f"🆕 Bugungi yangiliklar: **{today_news}**\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📈 **Kategoriyalar:**\n\n"
    )
    
    for category, count in category_stats.items():
        emoji = category_emojis.get(category, '📌')
        stats_text += f"{emoji} {category.capitalize()}: **{count}**\n"
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Qidirish"""
    if not context.args:
        await update.message.reply_text(
            "🔍 **QIDIRISH**\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "**Foydalanish:**\n"
            "`/search [so'z]`\n\n"
            "**Misol:**\n"
            "🔹 `/search prezident`\n"
            "🔹 `/search dollar`\n"
            "🔹 `/search sport`",
            parse_mode='Markdown'
        )
        return
    
    search_query = " ".join(context.args).lower()
    
    from db.models import News
    async with async_session() as session:
        result = await session.execute(select(News))
        all_news = result.scalars().all()
        
        found_news = [
            news for news in all_news 
            if search_query in news.text.lower()
        ]
    
    if not found_news:
        await update.message.reply_text(
            f"🔍 **QIDIRUV NATIJALARI**\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"❌ '{search_query}' bo'yicha hech narsa topilmadi.\n\n"
            f"💡 Boshqa so'z bilan qidiring.",
            parse_mode='Markdown'
        )
        return
    
    found_news = found_news[:3]
    
    category_emojis = {
        'siyosat': '🏛',
        'iqtisod': '💰',
        'jamiyat': '👥',
        'sport': '⚽',
        'texnologiya': '💻',
        'dunyo': '🌍',
        'salomatlik': '🏥',
        'obhavo': '🌤'
    }
    
    await update.message.reply_text(
        f"🔍 **QIDIRUV NATIJALARI**\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✅ Topildi: **{len(found_news)}** ta yangilik\n\n"
        f"🔎 So'rov: _{search_query}_",
        parse_mode='Markdown'
    )
    
    for i, news in enumerate(found_news, 1):
        emoji = category_emojis.get(news.category, '📌')
        text = f"{emoji} **{news.category.upper()}**\n\n{news.text}"
        
        if len(text) > 4000:
            text = text[:4000] + "..."
        
        await update.message.reply_text(text, parse_mode='Markdown')

async def handle_keyboard_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reply keyboard tugmalarini qayta ishlash"""
    text = update.message.text
    telegram_id = update.effective_user.id
    
    # Avval user va kategoriya tekshiruvi
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await update.message.reply_text(
                "❌ Avval /start ni bosing!",
                parse_mode='Markdown'
            )
            return
        
        lang = user.language
        
        # Kategoriya tanlanganligini tekshirish
        result = await session.execute(
            select(UserInterest).where(UserInterest.user_id == user.id)
        )
        interests = result.scalars().all()
        
        # Admin uchun cheklov yo'q
        username = update.effective_user.username
        is_admin = (username == ADMIN_USERNAME)
        
        # Agar kategoriya tanlanmagan bo'lsa - faqat Tariflar va Yordam ishlaydi
        from utils.translations import get_text
        from utils.i18n import t
        
        if not interests and not is_admin and text not in [t('btn_plans', lang), get_text('btn_help', lang), get_text('btn_language', lang)]:
            # Kategoriya tanlanmagan - Boshlash tugmasini bosish kerak
            if lang == 'uz':
                msg = "👇 **Boshlash** tugmasini bosing yoki /start buyrug'ini yuboring."
            elif lang == 'uz_cyrl':
                msg = "👇 **Бошлаш** тугмасини босинг ёки /start буйруғини юборинг."
            elif lang == 'ru':
                msg = "👇 Нажмите кнопку **Начать** или отправьте команду /start."
            else:  # en
                msg = "👇 Click the **Start** button or send /start command."
            
            await update.message.reply_text(msg, parse_mode='Markdown')
            return
    
    # Til tugmasi (barcha tillarda)
    from utils.translations import get_text, LANGUAGES
    
    if text == get_text('btn_language', lang):
        # Til tanlash (2x2 format)
        keyboard = [
            [
                InlineKeyboardButton("��🇿 O'zbek", callback_data="set_lang_uz"),
                InlineKeyboardButton("🇺🇿 Ўзбек", callback_data="set_lang_uz_cyrl")
            ],
            [
                InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru"),
                InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en")
            ]
        ]
        
        await update.message.reply_text(
            get_text('select_language', lang),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    # Qiziqishlar tugmasi
    if text == get_text('btn_interests', lang):
        await interests_command(update, context)
        return
    
    # Status tugmasi
    if text == get_text('btn_status', lang):
        await status_command(update, context)
        return
    
    # Yordam tugmasi
    if text == get_text('btn_help', lang):
        await help_command(update, context)
        return
    
    # Tariflar tugmasi (ko'p tillilik bilan)
    from utils.i18n import t
    if text == t('btn_plans', lang):
        # Tariflar ro'yxatini ko'rsatish
        telegram_id = update.effective_user.id
        
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                await update.message.reply_text(
                    t('error_generic', lang),
                    parse_mode='Markdown'
                )
                return
            
            # Hozirgi tarif
            has_trial = user.trial_end and user.trial_end > datetime.utcnow()
            has_subscription = user.subscription_end and user.subscription_end > datetime.utcnow()
            
            current_plan = f"🎁 {t('trial', lang)}"
            if has_subscription:
                plan_info = SUBSCRIPTION_PLANS.get(user.subscription_plan, SUBSCRIPTION_PLANS['basic'])
                current_plan = f"{plan_info['emoji']} {plan_info['name']}"
            
            text = (
                f"**{t('subscription_plans_header', lang)}**\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📌 **{t('current_plan', lang)}:** {current_plan}\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                f"{t('which_plan', lang)}\n\n"
            )
            
            keyboard = []
            for plan_key, plan_info in SUBSCRIPTION_PLANS.items():
                # Kategoriya limiti
                if plan_info.get('category_limit'):
                    limit_text = t('plan_categories', lang, limit=f"{plan_info['category_limit']}")
                else:
                    limit_text = t('plan_categories', lang, limit=t('unlimited', lang))
                
                text += (
                    f"{plan_info['emoji']} **{plan_info['name']}**\n"
                    f"   {t('plan_price', lang, price=plan_info['price'])}\n"
                    f"   {limit_text}\n"
                    f"   {t('plan_duration', lang, days=plan_info['duration_days'])}\n\n"
                )
                keyboard.append([
                    InlineKeyboardButton(
                        f"{plan_info['emoji']} {plan_info['name']} — {plan_info['price']:,}",
                        callback_data=f"select_plan_{plan_key}"
                    )
                ])
            
            text += "━━━━━━━━━━━━━━━━━━━━\n\n"
            
            # "Tarifni tanlang" tugmasi
            if lang == 'uz':
                text += "👇 Tarifni tanlang:"
            elif lang == 'uz_cyrl':
                text += "👇 Тарифни танланг:"
            elif lang == 'ru':
                text += "👇 Выберите тариф:"
            else:  # en
                text += "👇 Choose a plan:"
            
            await update.message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        return
    
    # Admin tugmalari (ko'p tillilik bilan)
    from utils.i18n import t
    if text == t('btn_statistics', lang):
        await stats_command(update, context)
        return
    
    if text == t('btn_admin_panel', lang):
        from bot.admin_handlers import admin_panel_command
        await admin_panel_command(update, context)
        return

async def activate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Obunani faollashtirish"""
    username = update.effective_user.username
    if username != ADMIN_USERNAME:
        await update.message.reply_text("❌ Bu buyruq faqat admin uchun.")
        return
    
    if len(context.args) != 2:
        await update.message.reply_text(
            "❌ **Noto'g'ri format**\n\n"
            "**Foydalanish:**\n"
            "`/activate <user_id> <plan>`\n\n"
            "**Misol:**\n"
            "`/activate 123456789 basic`\n"
            "`/activate 123456789 premium`",
            parse_mode='Markdown'
        )
        return
    
    try:
        user_telegram_id = int(context.args[0])
        plan_key = context.args[1]
    except:
        await update.message.reply_text("❌ User ID raqam bo'lishi kerak!")
        return
    
    if plan_key not in SUBSCRIPTION_PLANS:
        await update.message.reply_text(
            f"❌ Noto'g'ri plan: `{plan_key}`\n\n"
            f"Mavjud planlar: `basic`, `premium`",
            parse_mode='Markdown'
        )
        return
    
    plan_info = SUBSCRIPTION_PLANS[plan_key]
    
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await update.message.reply_text(f"❌ User topilmadi: `{user_telegram_id}`", parse_mode='Markdown')
            return
        
        user.subscription_plan = plan_key
        user.subscription_end = datetime.utcnow() + timedelta(days=plan_info['duration_days'])
        user.is_subscribed = True
        await session.commit()
        
        username_display = user.username or "yo'q"
        end_date_formatted = user.subscription_end.strftime('%d.%m.%Y %H:%M')
        
        await update.message.reply_text(
            f"✅ **OBUNA FAOLLASHTIRILDI**\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 User: {username_display}\n"
            f"🆔 ID: `{user_telegram_id}`\n\n"
            f"{plan_info['emoji']} **Plan:** {plan_info['name']}\n"
            f"💰 **Narx:** {plan_info['price']:,} so'm\n"
            f"⏰ **Muddat:** {plan_info['duration_days']} kun\n\n"
            f"📅 **Tugash sanasi:**\n"
            f"{end_date_formatted}",
            parse_mode='Markdown'
        )
        
        try:
            from bot.bot import bot
            if bot:
                await bot.app.bot.send_message(
                    chat_id=user_telegram_id,
                    text=(
                        f"🎉 **OBUNA FAOLLASHTIRILDI!**\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"{plan_info['emoji']} **Plan:** {plan_info['name']}\n"
                        f"⏰ **Muddat:** {plan_info['duration_days']} kun\n\n"
                        f"Endi barcha yangiliklar sizga avtomatik keladi!\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"📰 /interests — Yangiliklar\n"
                        f"👤 /status — Profilim"
                    ),
                    parse_mode='Markdown'
                )
        except:
            pass

async def latest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Placeholder"""
    pass

async def keywords_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Placeholder"""
    pass

async def breaking_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Placeholder"""
    pass

# -*- coding: utf-8 -*-
"""
Admin panel handlers - faqat @Murodjon_PM uchun
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy import select
from db.models import User, Channel, News, UserInterest
from db.database import async_session
from config import ADMIN_USERNAME, SUBSCRIPTION_PLANS, CHANNELS_TO_MONITOR
from datetime import datetime

def is_admin(username: str) -> bool:
    """Admin ekanligini tekshirish"""
    return username == ADMIN_USERNAME

async def send_admin_message(update: Update, text: str, parse_mode: str = 'Markdown'):
    """Admin xabarini reply keyboard bilan yuborish"""
    from bot.handlers import get_main_keyboard
    
    await update.message.reply_text(
        text,
        reply_markup=get_main_keyboard(is_admin=True),
        parse_mode=parse_mode
    )

async def admin_panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /admin - Admin panel
    """
    username = update.effective_user.username
    
    if not is_admin(username):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    text = (
        "🔐 **ADMIN PANEL**\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📊 **Statistika:**\n"
        "/stats — To'liq statistika\n\n"
        "📺 **Kanallar:**\n"
        "/channels — Kanallar ro'yxati\n"
        "/add\\_channel — Kanal qo'shish\n"
        "/remove\\_channel — Kanal o'chirish\n\n"
        "💰 **Tariflar:**\n"
        "/plans — Tariflar ro'yxati\n"
        "/add\\_plan — Tarif qo'shish\n"
        "/edit\\_plan — Tarifni o'zgartirish\n"
        "/remove\\_plan — Tarifni o'chirish\n\n"
        "🌐 **Tillar:**\n"
        "/languages — Tillar ro'yxati\n"
        "/add\\_language — Til qo'shish\n"
        "/remove\\_language — Til o'chirish\n\n"
        "👥 **Foydalanuvchilar:**\n"
        "/users — Barcha userlar\n"
        "/activate — Obuna berish\n"
        "/delete\\_user — User o'chirish\n\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def channels_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /channels - Kanallar ro'yxati
    """
    username = update.effective_user.username
    
    if not is_admin(username):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    async with async_session() as session:
        result = await session.execute(select(Channel))
        channels = result.scalars().all()
    
    if not channels:
        text = (
            "📺 **KANALLAR**\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Hozircha kanallar yo'q.\n\n"
            "Kanal qo'shish:\n"
            "`/add_channel @username`"
        )
    else:
        text = (
            "📺 **KANALLAR**\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        
        for i, channel in enumerate(channels, 1):
            status = "🟢 Faol" if channel.is_active else "🔴 O'chirilgan"
            # @ belgisini escape qilish
            text += f"{i}. `@{channel.username}`\n"
            text += f"   {status}\n\n"
        
        text += (
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "**Buyruqlar:**\n"
            "`/add_channel @username` — Qo'shish\n"
            "`/remove_channel @username` — O'chirish"
        )
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def add_channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /add_channel @username - Yangi kanal qo'shish (avtomatik)
    """
    username = update.effective_user.username
    
    if not is_admin(username):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ **Noto'g'ri format**\n\n"
            "**Foydalanish:**\n"
            "`/add_channel @username`\n\n"
            "**Misol:**\n"
            "`/add_channel @bbcnews`",
            parse_mode='Markdown'
        )
        return
    
    channel_username = context.args[0].replace('@', '')
    
    async with async_session() as session:
        # Kanal mavjudligini tekshirish
        result = await session.execute(
            select(Channel).where(Channel.username == channel_username)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            await update.message.reply_text(
                f"❌ @{channel_username} allaqachon mavjud!"
            )
            return
        
        # Yangi kanal qo'shish
        new_channel = Channel(
            username=channel_username,
            is_active=True
        )
        session.add(new_channel)
        await session.commit()
    
    # config.py ga avtomatik qo'shish
    try:
        import re
        
        # config.py ni o'qish
        with open('config.py', 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # CHANNELS_TO_MONITOR ni topish
        pattern = r"CHANNELS_TO_MONITOR\s*=\s*\[(.*?)\]"
        match = re.search(pattern, config_content, re.DOTALL)
        
        if match:
            channels_str = match.group(1)
            
            # Yangi kanal qo'shish
            # Oxirgi verguldan keyin qo'shish
            new_channel_line = f"\n    '@{channel_username}',"
            
            # Agar oxirgi element vergul bilan tugasa
            if channels_str.strip().endswith(','):
                new_channels_str = channels_str + new_channel_line + "\n"
            else:
                # Oxirgi elementga vergul qo'shish
                new_channels_str = channels_str.rstrip() + ',' + new_channel_line + "\n"
            
            # config.py ni yangilash
            new_config = config_content.replace(
                f"CHANNELS_TO_MONITOR = [{channels_str}]",
                f"CHANNELS_TO_MONITOR = [{new_channels_str}]"
            )
            
            # Faylga yozish
            with open('config.py', 'w', encoding='utf-8') as f:
                f.write(new_config)
            
            await update.message.reply_text(
                f"✅ **Kanal qo'shildi!**\n\n"
                f"@{channel_username}\n\n"
                f"✅ `config.py` ga avtomatik qo'shildi\n"
                f"✅ Bot qayta ishga tushirilmoqda...",
                parse_mode='Markdown'
            )
            
            # Botni qayta ishga tushirish
            await restart_bot_with_confirmation(update.effective_chat.id)
            
        else:
            await update.message.reply_text(
                f"✅ **Kanal database'ga qo'shildi!**\n\n"
                f"@{channel_username}\n\n"
                f"⚠️ **Qo'lda qo'shing:**\n"
                f"`config.py` da CHANNELS_TO_MONITOR ga qo'shing",
                parse_mode='Markdown'
            )
    
    except Exception as e:
        await update.message.reply_text(
            f"✅ **Kanal database'ga qo'shildi!**\n\n"
            f"@{channel_username}\n\n"
            f"⚠️ **Xato:**\n"
            f"`config.py` ga avtomatik qo'shib bo'lmadi: {e}\n\n"
            f"Qo'lda qo'shing: `config.py` da CHANNELS_TO_MONITOR",
            parse_mode='Markdown'
        )

async def remove_channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /remove_channel @username - Kanalni o'chirish (avtomatik)
    """
    username = update.effective_user.username
    
    if not is_admin(username):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ **Noto'g'ri format**\n\n"
            "**Foydalanish:**\n"
            "`/remove_channel @username`",
            parse_mode='Markdown'
        )
        return
    
    channel_username = context.args[0].replace('@', '')
    
    async with async_session() as session:
        result = await session.execute(
            select(Channel).where(Channel.username == channel_username)
        )
        channel = result.scalar_one_or_none()
        
        if not channel:
            await update.message.reply_text(
                f"❌ @{channel_username} topilmadi!"
            )
            return
        
        # Kanalni o'chirish
        await session.delete(channel)
        await session.commit()
    
    # config.py dan avtomatik o'chirish
    try:
        import re
        
        # config.py ni o'qish
        with open('config.py', 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # Kanalni o'chirish
        # Har xil formatlarni qo'llab-quvvatlash
        patterns = [
            # '@channel_username',  (vergul bilan)
            rf"\s*'@{re.escape(channel_username)}',\s*(?:#[^\n]*)?\n",
            rf'\s*"@{re.escape(channel_username)}",\s*(?:#[^\n]*)?\n',
            # '@channel_username'  (vergulsiz, oxirgi element)
            rf"\s*'@{re.escape(channel_username)}'\s*(?:#[^\n]*)?\n",
            rf'\s*"@{re.escape(channel_username)}"\s*(?:#[^\n]*)?\n',
        ]
        
        new_config = config_content
        for pattern in patterns:
            new_config = re.sub(pattern, '', new_config)
        
        # Agar oxirgi element o'chirilgan bo'lsa, oldingi elementdan vergulni olib tashlash
        # ,\n] → \n]
        new_config = re.sub(r',(\s*)\]', r'\1]', new_config)
        
        # Faylga yozish
        with open('config.py', 'w', encoding='utf-8') as f:
            f.write(new_config)
        
        await update.message.reply_text(
            f"✅ **Kanal o'chirildi!**\n\n"
            f"@{channel_username}\n\n"
            f"✅ `config.py` dan avtomatik o'chirildi\n"
            f"✅ Bot qayta ishga tushirilmoqda...",
            parse_mode='Markdown'
        )
        
        # Botni qayta ishga tushirish
        await restart_bot_with_confirmation(update.effective_chat.id)
        
    except Exception as e:
        await update.message.reply_text(
            f"✅ **Kanal database'dan o'chirildi!**\n\n"
            f"@{channel_username}\n\n"
            f"⚠️ **Xato:**\n"
            f"`config.py` dan avtomatik o'chirib bo'lmadi: {e}\n\n"
            f"Qo'lda o'chiring: `config.py` da CHANNELS_TO_MONITOR",
            parse_mode='Markdown'
        )

async def plans_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /plans - Tariflar ro'yxati
    """
    username = update.effective_user.username
    
    if not is_admin(username):
        await send_admin_message(update, "❌ Sizda admin huquqi yo'q.")
        return
    
    text = "💰 **TARIFLAR**\n\n"
    
    for plan_key, plan_info in SUBSCRIPTION_PLANS.items():
        text += f"{plan_info['emoji']} **{plan_info['name']}:** {plan_info['price']:,} so'm\n"
    
    text += (
        "\n━━━━━━━━━━━━━━━━━━━━\n\n"
        "**Narx o'zgartirish:**\n"
        "`/set_price [plan] [narx]`\n\n"
        "**Misol:**\n"
        "`/set_price basic 10000`"
    )
    
    await send_admin_message(update, text)

async def set_price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /set_price <plan> <narx> - Tarif narxini o'zgartirish (avtomatik)
    """
    username = update.effective_user.username
    
    if not is_admin(username):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    if len(context.args) != 2:
        await update.message.reply_text(
            "❌ **Noto'g'ri format**\n\n"
            "**Foydalanish:**\n"
            "`/set_price [plan] [narx]`\n\n"
            "**Misol:**\n"
            "`/set_price basic 10000`\n"
            "`/set_price premium 20000`",
            parse_mode='Markdown'
        )
        return
    
    plan_key = context.args[0]
    try:
        new_price = int(context.args[1])
    except:
        await update.message.reply_text("❌ Narx raqam bo'lishi kerak!")
        return
    
    if plan_key not in SUBSCRIPTION_PLANS:
        await update.message.reply_text(
            f"❌ Noto'g'ri plan: `{plan_key}`\n\n"
            f"Mavjud planlar: `basic`, `premium`",
            parse_mode='Markdown'
        )
        return
    
    # config.py ni avtomatik o'zgartirish
    try:
        import re
        
        # config.py ni o'qish
        with open('config.py', 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # Narxni topish va o'zgartirish
        # 'basic': { ... 'price': 7000, ... } → 'price': 10000
        pattern = rf"('{plan_key}':\s*\{{[^}}]*'price':\s*)\d+"
        
        # Eski narxni topish
        old_match = re.search(pattern, config_content)
        if not old_match:
            await update.message.reply_text(
                f"❌ **Xato:**\n\n"
                f"config.py da {plan_key} topilmadi",
                parse_mode='Markdown'
            )
            return
        
        # Yangi narx bilan almashtirish
        new_config = re.sub(pattern, rf"\g<1>{new_price}", config_content)
        
        # Faylga yozish
        with open('config.py', 'w', encoding='utf-8') as f:
            f.write(new_config)
        
        await update.message.reply_text(
            f"✅ **Narx o'zgartirildi!**\n\n"
            f"📦 **Plan:** {plan_key}\n"
            f"💰 **Yangi narx:** {new_price:,} so'm\n\n"
            f"✅ config.py avtomatik yangilandi\n"
            f"✅ Bot qayta ishga tushirilmoqda...",
            parse_mode='Markdown'
        )
        
        # Botni qayta ishga tushirish
        await restart_bot_with_confirmation(update.effective_chat.id)
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ **Xato:**\n\n"
            f"config.py ni o'zgartirib bo'lmadi: {e}\n\n"
            f"**Qo'lda o'zgartiring:**\n"
            f"1. config.py ni oching\n"
            f"2. SUBSCRIPTION_PLANS da {plan_key} ni toping\n"
            f"3. price ni {new_price} ga o'zgartiring\n"
            f"4. Botni qayta ishga tushiring",
            parse_mode='Markdown'
        )

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /users - Barcha foydalanuvchilar (tarif va qolgan kunlar bilan)
    """
    username = update.effective_user.username
    
    if not is_admin(username):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
    
    # Statistika
    total = len(users)
    trial_active = sum(1 for u in users if u.trial_end and u.trial_end > datetime.utcnow())
    subscribed = sum(1 for u in users if u.subscription_end and u.subscription_end > datetime.utcnow())
    expired = total - trial_active - subscribed
    
    text = (
        "👥 **FOYDALANUVCHILAR**\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 **Statistika:**\n"
        f"   Jami: {total}\n"
        f"   🎁 Trial: {trial_active}\n"
        f"   ⭐ Obuna: {subscribed}\n"
        f"   ⏰ Tugagan: {expired}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "**Oxirgi 10 ta user:**\n\n"
    )
    
    # Oxirgi 10 ta user
    recent_users = sorted(users, key=lambda u: u.created_at, reverse=True)[:10]
    
    for i, user in enumerate(recent_users, 1):
        # Tarif va qolgan kunlarni aniqlash
        now = datetime.utcnow()
        
        if user.subscription_end and user.subscription_end > now:
            # Pullik obuna
            days_left = (user.subscription_end - now).days
            plan_name = user.subscription_plan or 'unknown'
            
            # Plan emoji
            plan_emoji = "⭐"
            if plan_name == 'basic':
                plan_emoji = "📦"
            elif plan_name == 'premium':
                plan_emoji = "⭐"
            
            status = f"{plan_emoji} {plan_name.capitalize()} ({days_left} kun)"
        elif user.trial_end and user.trial_end > now:
            # Trial
            days_left = (user.trial_end - now).days
            status = f"🎁 Trial ({days_left} kun)"
        else:
            # Tugagan
            status = "⏰ Tugagan"
        
        username_str = f"`@{user.username}`" if user.username else "No username"
        text += f"{i}. {username_str}\n"
        text += f"   ID: `{user.telegram_id}`\n"
        text += f"   Tarif: {status}\n\n"
    
    # Inline keyboard - user o'chirish
    keyboard = [
        [InlineKeyboardButton("🗑 User o'chirish", callback_data="delete_user_prompt")]
    ]
    
    await update.message.reply_text(
        text, 
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def add_plan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /add_plan <key> <name> <price> <days> <limit> - Yangi tarif qo'shish
    """
    username = update.effective_user.username
    
    if not is_admin(username):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    if len(context.args) != 5:
        await update.message.reply_text(
            "❌ Noto'g'ri format\n\n"
            "Foydalanish:\n"
            "/add_plan key name price days limit\n\n"
            "Misol:\n"
            "/add_plan vip VIP 30000 30 unlimited\n"
            "/add_plan starter Starter 5000 30 2\n\n"
            "Limit:\n"
            "- Raqam (2, 3, 5)\n"
            "- unlimited yoki cheksiz"
        )
        return
        return
    
    plan_key = context.args[0]
    plan_name = context.args[1]
    
    try:
        plan_price = int(context.args[2])
        plan_days = int(context.args[3])
    except:
        await update.message.reply_text("❌ Narx va muddat raqam bo'lishi kerak!")
        return
    
    # Limit
    limit_str = context.args[4].lower()
    if limit_str == 'unlimited' or limit_str == 'cheksiz':
        plan_limit = None
    else:
        try:
            plan_limit = int(limit_str)
        except:
            await update.message.reply_text("❌ Limit raqam yoki 'unlimited' bo'lishi kerak!")
            return
    
    # config.py ga qo'shish
    try:
        import re
        
        # config.py ni o'qish
        with open('config.py', 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # SUBSCRIPTION_PLANS ni topish
        pattern = r"SUBSCRIPTION_PLANS\s*=\s*\{(.*?)\n\}"
        match = re.search(pattern, config_content, re.DOTALL)
        
        if match:
            plans_str = match.group(1)
            
            # Oxirgi vergulni olib tashlash (agar bo'lsa)
            plans_str_clean = plans_str.rstrip()
            if plans_str_clean.endswith(','):
                # Oxirgi vergulni olib tashlash
                last_comma_pos = plans_str.rfind(',')
                plans_str = plans_str[:last_comma_pos] + plans_str[last_comma_pos+1:]
            
            # Yangi tarif qo'shish
            emoji = "💎"  # Default emoji
            new_plan = f""",
    '{plan_key}': {{
        'name': '{plan_name}',
        'price': {plan_price},
        'duration_days': {plan_days},
        'emoji': '{emoji}',
        'category_limit': {plan_limit if plan_limit is not None else 'None'}  # {'Cheksiz' if plan_limit is None else f'{plan_limit} ta kategoriya'}
    }}"""
            
            # Oxirgi tarif dan keyin qo'shish
            new_plans_str = plans_str + new_plan
            
            # config.py ni yangilash
            new_config = config_content.replace(
                f"SUBSCRIPTION_PLANS = {{{plans_str}\n}}",
                f"SUBSCRIPTION_PLANS = {{{new_plans_str}\n}}"
            )
            
            # Faylga yozish
            with open('config.py', 'w', encoding='utf-8') as f:
                f.write(new_config)
            
            limit_text = "Cheksiz" if plan_limit is None else f"{plan_limit} ta"
            
            await update.message.reply_text(
                f"✅ **Tarif qo'shildi!**\n\n"
                f"{emoji} **{plan_name}**\n"
                f"   Key: `{plan_key}`\n"
                f"   💰 Narx: {plan_price:,} so'm\n"
                f"   ⏰ Muddat: {plan_days} kun\n"
                f"   📰 Kategoriya: {limit_text}\n\n"
                f"✅ `config.py` ga avtomatik qo'shildi\n"
                f"✅ Bot qayta ishga tushirilmoqda...",
                parse_mode='Markdown'
            )
            
            # Botni qayta ishga tushirish
            await restart_bot_with_confirmation(update.effective_chat.id)
            
        else:
            await update.message.reply_text(
                f"❌ **Xato:**\n\n"
                f"`config.py` da SUBSCRIPTION_PLANS topilmadi",
                parse_mode='Markdown'
            )
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ **Xato:**\n\n"
            f"`config.py` ga qo'shib bo'lmadi: {e}",
            parse_mode='Markdown'
        )

async def edit_plan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /edit_plan <key> <price> <limit> - Tarifni o'zgartirish
    """
    username = update.effective_user.username
    
    if not is_admin(username):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    if len(context.args) != 3:
        await update.message.reply_text(
            "❌ **Noto'g'ri format**\n\n"
            "**Foydalanish:**\n"
            "`/edit_plan <key> <price> <limit>`\n\n"
            "**Misol:**\n"
            "`/edit_plan premium 20000 unlimited`\n"
            "`/edit_plan basic 10000 5`\n\n"
            "**Limit:**\n"
            "- Raqam (masalan: 2, 3, 5)\n"
            "- `unlimited` - cheksiz",
            parse_mode='Markdown'
        )
        return
    
    plan_key = context.args[0]
    
    try:
        new_price = int(context.args[1])
    except:
        await update.message.reply_text("❌ Narx raqam bo'lishi kerak!")
        return
    
    # Limit
    limit_str = context.args[2].lower()
    if limit_str == 'unlimited' or limit_str == 'cheksiz':
        new_limit = None
    else:
        try:
            new_limit = int(limit_str)
        except:
            await update.message.reply_text("❌ Limit raqam yoki 'unlimited' bo'lishi kerak!")
            return
    
    # config.py ni o'zgartirish
    try:
        import re
        
        # config.py ni o'qish
        with open('config.py', 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # Tarifni topish va o'zgartirish
        # 'price': 15000 → 'price': 20000
        price_pattern = rf"('{plan_key}':\s*\{{[^}}]*'price':\s*)\d+"
        config_content = re.sub(price_pattern, rf"\g<1>{new_price}", config_content)
        
        # 'category_limit': 3 → 'category_limit': 5
        # 'category_limit': None → 'category_limit': 5
        limit_value = new_limit if new_limit is not None else 'None'
        limit_pattern = rf"('{plan_key}':\s*\{{[^}}]*'category_limit':\s*)(None|\d+)"
        config_content = re.sub(limit_pattern, rf"\g<1>{limit_value}", config_content)
        
        # Faylga yozish
        with open('config.py', 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        limit_text = "Cheksiz" if new_limit is None else f"{new_limit} ta"
        
        await update.message.reply_text(
            f"✅ **Tarif o'zgartirildi!**\n\n"
            f"**Plan:** `{plan_key}`\n"
            f"   💰 Yangi narx: {new_price:,} so'm\n"
            f"   📰 Yangi limit: {limit_text}\n\n"
            f"✅ `config.py` avtomatik yangilandi\n"
            f"✅ Bot qayta ishga tushirilmoqda...",
            parse_mode='Markdown'
        )
        
        # Botni qayta ishga tushirish
        await restart_bot_with_confirmation(update.effective_chat.id)
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ **Xato:**\n\n"
            f"`config.py` ni o'zgartirib bo'lmadi: {e}",
            parse_mode='Markdown'
        )

async def remove_plan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /remove_plan <key> - Tarifni o'chirish
    """
    username = update.effective_user.username
    
    if not is_admin(username):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    if len(context.args) != 1:
        await update.message.reply_text(
            "❌ **Noto'g'ri format**\n\n"
            "**Foydalanish:**\n"
            "`/remove_plan <key>`\n\n"
            "**Misol:**\n"
            "`/remove_plan vip`",
            parse_mode='Markdown'
        )
        return
    
    plan_key = context.args[0]
    
    # config.py dan o'chirish
    try:
        import re
        
        # config.py ni o'qish
        with open('config.py', 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # Tarifni o'chirish
        # 'key': {...}, ni topish va o'chirish
        pattern = rf"\s*'{plan_key}':\s*\{{[^}}]*\}},?\n"
        new_config = re.sub(pattern, '', config_content)
        
        # Faylga yozish
        with open('config.py', 'w', encoding='utf-8') as f:
            f.write(new_config)
        
        await update.message.reply_text(
            f"✅ **Tarif o'chirildi!**\n\n"
            f"**Plan:** `{plan_key}`\n\n"
            f"✅ `config.py` dan avtomatik o'chirildi\n"
            f"✅ Bot qayta ishga tushirilmoqda...",
            parse_mode='Markdown'
        )
        
        # Botni qayta ishga tushirish
        await restart_bot_with_confirmation(update.effective_chat.id)
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ **Xato:**\n\n"
            f"`config.py` dan o'chirib bo'lmadi: {e}",
            parse_mode='Markdown'
        )


async def delete_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    User o'chirish callback handler
    """
    query = update.callback_query
    await query.answer()
    
    data = query.data
    username = update.effective_user.username
    
    if not is_admin(username):
        await query.answer("❌ Sizda admin huquqi yo'q.", show_alert=True)
        return
    
    if data == "delete_user_prompt":
        # User ID so'rash
        text = (
            "🗑 **USER O'CHIRISH**\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "User ID ni yuboring:\n\n"
            "**Format:**\n"
            "`/delete_user <telegram_id>`\n\n"
            "**Misol:**\n"
            "`/delete_user 123456789`\n\n"
            "⚠️ **Ogohlantirish:**\n"
            "User va uning barcha ma'lumotlari (qiziqishlar, yangiliklar) o'chiriladi!"
        )
        
        try:
            await query.edit_message_text(text, parse_mode='Markdown')
        except:
            pass
        return
    
    if data.startswith("confirm_delete_"):
        # User o'chirishni tasdiqlash
        telegram_id = int(data.replace("confirm_delete_", ""))
        
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                await query.answer("❌ User topilmadi!", show_alert=True)
                return
            
            # User va uning barcha ma'lumotlarini o'chirish
            # UserInterest lar avtomatik o'chiriladi (cascade='all, delete-orphan')
            await session.delete(user)
            await session.commit()
            
            text = (
                "✅ **USER O'CHIRILDI!**\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                f"**Telegram ID:** `{telegram_id}`\n"
                f"**Username:** `@{user.username if user.username else 'No username'}`\n\n"
                "✅ User va barcha ma'lumotlari o'chirildi"
            )
            
            try:
                await query.edit_message_text(text, parse_mode='Markdown')
            except:
                pass
        return
    
    if data.startswith("cancel_delete_"):
        # Bekor qilish
        text = "❌ **Bekor qilindi**"
        
        try:
            await query.edit_message_text(text)
        except:
            pass
        return

async def delete_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /delete_user <telegram_id> - Userni o'chirish
    """
    username = update.effective_user.username
    
    if not is_admin(username):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    if len(context.args) != 1:
        await update.message.reply_text(
            "❌ **Noto'g'ri format**\n\n"
            "**Foydalanish:**\n"
            "`/delete_user <telegram_id>`\n\n"
            "**Misol:**\n"
            "`/delete_user 123456789`",
            parse_mode='Markdown'
        )
        return
    
    try:
        telegram_id = int(context.args[0])
    except:
        await update.message.reply_text("❌ Telegram ID raqam bo'lishi kerak!")
        return
    
    # User mavjudligini tekshirish
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await update.message.reply_text(
                f"❌ **User topilmadi!**\n\n"
                f"Telegram ID: `{telegram_id}`",
                parse_mode='Markdown'
            )
            return
        
        # Tarif ma'lumotlari
        now = datetime.utcnow()
        
        if user.subscription_end and user.subscription_end > now:
            days_left = (user.subscription_end - now).days
            plan_name = user.subscription_plan or 'unknown'
            status = f"⭐ {plan_name.capitalize()} ({days_left} kun)"
        elif user.trial_end and user.trial_end > now:
            days_left = (user.trial_end - now).days
            status = f"🎁 Trial ({days_left} kun)"
        else:
            status = "⏰ Tugagan"
        
        # Qiziqishlar soni
        result_interests = await session.execute(
            select(UserInterest).where(UserInterest.user_id == user.id)
        )
        interests = result_interests.scalars().all()
        interests_count = len(interests)
        
        text = (
            "⚠️ **USER O'CHIRISH**\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"**Telegram ID:** `{telegram_id}`\n"
            f"**Username:** `@{user.username if user.username else 'No username'}`\n"
            f"**Tarif:** {status}\n"
            f"**Qiziqishlar:** {interests_count} ta\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "⚠️ **Ogohlantirish:**\n"
            "User va uning barcha ma'lumotlari (qiziqishlar, yangiliklar) o'chiriladi!\n\n"
            "Davom ettirasizmi?"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Ha, o'chirish", callback_data=f"confirm_delete_{telegram_id}"),
                InlineKeyboardButton("❌ Yo'q", callback_data=f"cancel_delete_{telegram_id}")
            ]
        ]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )


async def languages_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /languages - Tillar ro'yxati
    """
    username = update.effective_user.username
    
    if not is_admin(username):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    from utils.translations import LANGUAGES
    
    text = (
        "🌐 **TILLAR**\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "**Mavjud tillar:**\n\n"
    )
    
    for i, (lang_code, lang_name) in enumerate(LANGUAGES.items(), 1):
        text += f"{i}. `{lang_code}` — {lang_name}\n"
    
    text += (
        "\n━━━━━━━━━━━━━━━━━━━━\n\n"
        "**Buyruqlar:**\n"
        "`/add_language <code> <name>` — Qo'shish\n"
        "`/remove_language <code>` — O'chirish\n\n"
        "**Misol:**\n"
        "`/add_language tr 🇹🇷 Türkçe`\n"
        "`/remove_language en`"
    )
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def restart_bot_with_confirmation(chat_id: int, message_text: str = None):
    """
    Botni qayta ishga tushirish va tasdiqlash xabari yuborish
    
    Args:
        chat_id: Xabar yuboriladigan chat ID
        message_text: Qo'shimcha xabar matni (agar kerak bo'lsa)
    """
    import os
    import sys
    import asyncio
    from telegram import Bot
    from config import BOT_TOKEN
    
    # 2 soniya kutish (xabar yuborilishi uchun)
    await asyncio.sleep(2)
    
    # Botni qayta ishga tushirish
    os.execv(sys.executable, ['python'] + sys.argv)


async def add_language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /add_language <code> <name> - Yangi til qo'shish
    """
    username = update.effective_user.username
    
    if not is_admin(username):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ **Noto'g'ri format**\n\n"
            "**Foydalanish:**\n"
            "`/add_language <code> <name>`\n\n"
            "**Misol:**\n"
            "`/add_language tr 🇹🇷 Türkçe`\n"
            "`/add_language ar 🇸🇦 العربية`",
            parse_mode='Markdown'
        )
        return
    
    lang_code = context.args[0]
    lang_name = ' '.join(context.args[1:])
    
    # utils/translations.py ga qo'shish
    try:
        import re
        
        # translations.py ni o'qish
        with open('utils/translations.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # LANGUAGES ni topish
        pattern = r"LANGUAGES\s*=\s*\{(.*?)\n\}"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            languages_str = match.group(1)
            
            # Yangi til qo'shish
            new_lang = f"\n    '{lang_code}': '{lang_name}',"
            
            # Oxirgi verguldan keyin qo'shish
            new_languages_str = languages_str + new_lang + "\n"
            
            # translations.py ni yangilash
            new_content = content.replace(
                f"LANGUAGES = {{{languages_str}\n}}",
                f"LANGUAGES = {{{new_languages_str}}}"
            )
            
            # Faylga yozish
            with open('utils/translations.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            await update.message.reply_text(
                f"✅ **Til qo'shildi!**\n\n"
                f"**Kod:** `{lang_code}`\n"
                f"**Nom:** {lang_name}\n\n"
                f"✅ `utils/translations.py` ga avtomatik qo'shildi\n\n"
                f"⚠️ **Eslatma:**\n"
                f"Yangi til uchun tarjimalarni qo'lda qo'shishingiz kerak:\n"
                f"- `welcome`\n"
                f"- `select_interests`\n"
                f"- `categories`\n"
                f"- va boshqalar...\n\n"
                f"✅ Bot qayta ishga tushirilmoqda...",
                parse_mode='Markdown'
            )
            
            # Botni qayta ishga tushirish
            await restart_bot_with_confirmation(update.effective_chat.id)
            
        else:
            await update.message.reply_text(
                f"❌ **Xato:**\n\n"
                f"`utils/translations.py` da LANGUAGES topilmadi",
                parse_mode='Markdown'
            )
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ **Xato:**\n\n"
            f"`utils/translations.py` ga qo'shib bo'lmadi: {e}",
            parse_mode='Markdown'
        )

async def remove_language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /remove_language <code> - Tilni o'chirish
    """
    username = update.effective_user.username
    
    if not is_admin(username):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    if len(context.args) != 1:
        await update.message.reply_text(
            "❌ **Noto'g'ri format**\n\n"
            "**Foydalanish:**\n"
            "`/remove_language <code>`\n\n"
            "**Misol:**\n"
            "`/remove_language en`",
            parse_mode='Markdown'
        )
        return
    
    lang_code = context.args[0]
    
    # Asosiy tillarni o'chirishga ruxsat bermaslik
    protected_langs = ['uz', 'uz_cyrl', 'ru']
    if lang_code in protected_langs:
        await update.message.reply_text(
            f"❌ **Xato:**\n\n"
            f"`{lang_code}` tilini o'chirib bo'lmaydi!\n\n"
            f"Bu asosiy tillardan biri.",
            parse_mode='Markdown'
        )
        return
    
    # utils/translations.py dan o'chirish
    try:
        import re
        
        # translations.py ni o'qish
        with open('utils/translations.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Tilni o'chirish
        # 'code': 'name',  (vergul bilan)
        patterns = [
            rf"\s*'{re.escape(lang_code)}':\s*'[^']*',\s*\n",
            rf'\s*"{re.escape(lang_code)}":\s*"[^"]*",\s*\n',
        ]
        
        new_content = content
        for pattern in patterns:
            new_content = re.sub(pattern, '', new_content)
        
        # Faylga yozish
        with open('utils/translations.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        await update.message.reply_text(
            f"✅ **Til o'chirildi!**\n\n"
            f"**Kod:** `{lang_code}`\n\n"
            f"✅ `utils/translations.py` dan avtomatik o'chirildi\n"
            f"✅ Bot qayta ishga tushirilmoqda...",
            parse_mode='Markdown'
        )
        
        # Botni qayta ishga tushirish
        await restart_bot_with_confirmation(update.effective_chat.id)
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ **Xato:**\n\n"
            f"`utils/translations.py` dan o'chirib bo'lmadi: {e}",
            parse_mode='Markdown'
        )

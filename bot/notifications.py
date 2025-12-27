"""
User notifikatsiyalari
"""
from telegram import Bot
from config import BOT_TOKEN

async def send_trial_ending_notification(telegram_id: int, days_left: int):
    """Trial tugashiga yaqin xabar"""
    bot = Bot(token=BOT_TOKEN)
    
    message = (
        f"⏰ **Trial tugashiga {days_left} kun qoldi!**\n\n"
        f"Yangiliklar olishni davom ettirish uchun obuna bo'ling.\n\n"
        f"💳 **Obuna narxi:** 15,000 so'm/oy\n\n"
        f"Obuna bo'lish: /subscribe"
    )
    
    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=message,
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Trial notification xatolik: {e}")


async def send_trial_expired_notification(telegram_id: int):
    """Trial tugagan xabar"""
    bot = Bot(token=BOT_TOKEN)
    
    message = (
        f"❌ **Trial tugadi**\n\n"
        f"Yangiliklar olishni davom ettirish uchun obuna bo'ling.\n\n"
        f"💳 **Obuna narxi:** 15,000 so'm/oy\n\n"
        f"Obuna bo'lish: /subscribe"
    )
    
    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=message,
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Trial expired notification xatolik: {e}")

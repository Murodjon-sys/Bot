from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User
from config import TRIAL_DAYS

async def start_trial(session: AsyncSession, telegram_id: int):
    """User uchun trial boshlash"""
    user = await session.get(User, telegram_id)
    if user and not user.trial_end:
        user.trial_end = datetime.utcnow() + timedelta(days=TRIAL_DAYS)
        await session.commit()

async def is_user_active(session: AsyncSession, telegram_id: int) -> bool:
    """User aktiv yoki yo'qligini tekshirish"""
    user = await session.get(User, telegram_id)
    if not user:
        return False
    
    # Trial davri yoki subscription aktiv
    if user.is_subscribed:
        return True
    
    if user.trial_end and user.trial_end > datetime.utcnow():
        return True
    
    return False

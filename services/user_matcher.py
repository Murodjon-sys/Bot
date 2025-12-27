from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User, UserInterest
from datetime import datetime

async def get_matching_users(session: AsyncSession, category: str, news_text: str = "", is_breaking: bool = False) -> list:
    """
    Berilgan kategoriyaga qiziqadigan va aktiv userlarni topish
    
    Args:
        session: Database session
        category: Yangilik kategoriyasi
        news_text: Yangilik matni (ishlatilmaydi)
        is_breaking: Breaking news yoki yo'q (ishlatilmaydi)
    """
    # Trial yoki subscription aktiv bo'lgan userlar
    query = select(User).join(UserInterest).where(
        UserInterest.category == category,
        (User.trial_end > datetime.utcnow()) | (User.subscription_end > datetime.utcnow())
    )
    
    result = await session.execute(query)
    users = result.scalars().all()
    
    matching_user_ids = []
    
    for user in users:
        # Trial yoki subscription tekshiruvi
        has_trial = user.trial_end and user.trial_end > datetime.utcnow()
        has_subscription = user.subscription_end and user.subscription_end > datetime.utcnow()
        
        if not has_trial and not has_subscription:
            # Trial ham, subscription ham tugagan
            continue
        
        # Barcha aktiv userlar uchun yangilik yuborish (24/7)
        matching_user_ids.append(user.telegram_id)
    
    return matching_user_ids

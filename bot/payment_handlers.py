"""
To'lov bilan bog'liq handlerlar
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy import select
from db.models import User, Payment
from db.database import async_session
from config import SUBSCRIPTION_PLANS
from services.tspay import tspay, TSPayError
from utils.translations import get_text
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


async def show_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Tariflarni ko'rsatish
    """
    query = update.callback_query
    if query:
        await query.answer()
        message = query.message
        telegram_id = query.from_user.id
    else:
        message = update.message
        telegram_id = update.effective_user.id
    
    # User tilini olish
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        lang = user.language if user and user.language else 'uz'
    
    # Tariflar matni
    plans_text = get_text('plans_header', lang) + "\n\n"
    
    for plan_key, plan_info in SUBSCRIPTION_PLANS.items():
        limit_text = get_text('unlimited', lang) if plan_info.get('category_limit') is None else f"{plan_info['category_limit']} ta"
        
        plans_text += (
            f"{plan_info['emoji']} **{plan_info['name']}**\n"
            f"   💰 {get_text('price', lang)}: {plan_info['price']:,} {get_text('sum_month', lang)}\n"
            f"   📰 {get_text('categories', lang)}: {limit_text}\n"
            f"   ⏰ {get_text('duration', lang)}: {plan_info['duration_days']} {get_text('days', lang)}\n\n"
        )
    
    plans_text += "━━━━━━━━━━━━━━━━━━━━\n\n"
    plans_text += get_text('select_plan', lang)
    
    # Inline keyboard - har bir tarif uchun tugma
    keyboard = []
    for plan_key, plan_info in SUBSCRIPTION_PLANS.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{plan_info['emoji']} {plan_info['name']} — {plan_info['price']:,} so'm",
                callback_data=f"buy_{plan_key}"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        try:
            await message.edit_text(plans_text, parse_mode='Markdown', reply_markup=reply_markup)
        except:
            await message.reply_text(plans_text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await message.reply_text(plans_text, parse_mode='Markdown', reply_markup=reply_markup)


async def buy_plan_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Tarif sotib olish callback
    """
    query = update.callback_query
    await query.answer()
    
    telegram_id = query.from_user.id
    username = query.from_user.username
    data = query.data  # buy_basic yoki buy_premium
    
    plan_key = data.replace("buy_", "")
    plan_info = SUBSCRIPTION_PLANS.get(plan_key)
    
    if not plan_info:
        await query.message.reply_text("❌ Tarif topilmadi")
        return
    
    # User tilini olish
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await query.message.reply_text("❌ User topilmadi. /start bosing")
            return
        
        lang = user.language if user.language else 'uz'
        
        # To'lov yaratish
        try:
            # TSPay orqali to'lov yaratish
            amount = plan_info['price']
            description = f"{plan_info['name']} plan - @{username or telegram_id}"
            
            # Kutish xabari
            wait_msg = await query.message.reply_text(
                get_text('creating_payment', lang)
            )
            
            payment_url, transaction_id = tspay.create_payment(
                amount=amount,
                description=description,
                order_id=f"user_{user.id}_plan_{plan_key}"
            )
            
            # Database ga saqlash
            payment = Payment(
                user_id=user.id,
                amount=amount,
                plan=plan_key,
                transaction_id=transaction_id,
                payment_url=payment_url,
                status='pending'
            )
            session.add(payment)
            await session.commit()
            
            # Kutish xabarini o'chirish
            try:
                await wait_msg.delete()
            except:
                pass
            
            # To'lov havolasini yuborish
            payment_text = (
                f"💳 **{get_text('payment_created', lang)}**\n\n"
                f"{plan_info['emoji']} **{get_text('plan', lang)}:** {plan_info['name']}\n"
                f"💰 **{get_text('amount', lang)}:** {amount:,} {get_text('sum', lang)}\n"
                f"🆔 **{get_text('transaction_id', lang)}:** `{transaction_id}`\n\n"
                f"👇 {get_text('click_to_pay', lang)}"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    f"💳 {get_text('pay_now', lang)}",
                    url=payment_url
                )],
                [InlineKeyboardButton(
                    f"🔄 {get_text('check_payment', lang)}",
                    callback_data=f"check_payment_{transaction_id}"
                )]
            ])
            
            await query.message.reply_text(
                payment_text,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            
            logger.info(f"To'lov yaratildi: user={telegram_id}, plan={plan_key}, transaction={transaction_id}")
            
        except TSPayError as e:
            logger.error(f"TSPay xato: {e}")
            await query.message.reply_text(
                f"❌ {get_text('payment_error', lang)}\n\n"
                f"{get_text('try_again_later', lang)}"
            )
        except Exception as e:
            logger.error(f"To'lov yaratishda xato: {e}")
            import traceback
            traceback.print_exc()
            await query.message.reply_text(
                f"❌ {get_text('payment_error', lang)}"
            )


async def check_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    To'lov statusini tekshirish
    """
    query = update.callback_query
    await query.answer(get_text('checking_payment', 'uz'))
    
    telegram_id = query.from_user.id
    data = query.data  # check_payment_TRANSACTION_ID
    
    transaction_id = data.replace("check_payment_", "")
    
    async with async_session() as session:
        # User va payment topish
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await query.message.reply_text("❌ User topilmadi")
            return
        
        lang = user.language if user.language else 'uz'
        
        result = await session.execute(
            select(Payment).where(
                Payment.transaction_id == transaction_id,
                Payment.user_id == user.id
            )
        )
        payment = result.scalar_one_or_none()
        
        if not payment:
            await query.message.reply_text(
                get_text('payment_not_found', lang)
            )
            return
        
        # TSPay dan status tekshirish
        try:
            status = tspay.check_payment_status(transaction_id)
            
            # Database ni yangilash
            payment.status = status
            
            if status == 'success' and not payment.paid_at:
                # To'lov muvaffaqiyatli
                payment.paid_at = datetime.utcnow()
                
                # Obunani faollashtirish
                from datetime import timedelta
                plan_info = SUBSCRIPTION_PLANS[payment.plan]
                
                user.is_subscribed = True
                user.subscription_plan = payment.plan
                user.subscription_end = datetime.utcnow() + timedelta(days=plan_info['duration_days'])
                
                await session.commit()
                
                # Muvaffaqiyat xabari
                success_text = (
                    f"✅ **{get_text('payment_success', lang)}**\n\n"
                    f"{plan_info['emoji']} **{get_text('plan', lang)}:** {plan_info['name']}\n"
                    f"💰 **{get_text('amount', lang)}:** {payment.amount:,} {get_text('sum', lang)}\n"
                    f"📅 **{get_text('valid_until', lang)}:** {user.subscription_end.strftime('%d.%m.%Y')}\n\n"
                    f"🎉 {get_text('subscription_activated', lang)}"
                )
                
                await query.message.reply_text(success_text, parse_mode='Markdown')
                logger.info(f"Obuna faollashtirildi: user={telegram_id}, plan={payment.plan}")
                
            elif status == 'pending':
                await query.message.reply_text(
                    f"⏳ {get_text('payment_pending', lang)}\n\n"
                    f"{get_text('complete_payment', lang)}"
                )
            elif status == 'failed':
                await session.commit()
                await query.message.reply_text(
                    f"❌ {get_text('payment_failed', lang)}\n\n"
                    f"{get_text('try_again', lang)}"
                )
            elif status == 'cancelled':
                await session.commit()
                await query.message.reply_text(
                    f"🚫 {get_text('payment_cancelled', lang)}"
                )
            else:
                await query.message.reply_text(
                    f"❓ {get_text('payment_unknown', lang)}: {status}"
                )
                
        except TSPayError as e:
            logger.error(f"Status tekshirishda xato: {e}")
            await query.message.reply_text(
                f"❌ {get_text('check_error', lang)}"
            )

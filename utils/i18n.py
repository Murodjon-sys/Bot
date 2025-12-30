"""
🌍 Production-Ready Internationalization (i18n) System
Centralized translation management for multilingual Telegram bot
"""
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# SUPPORTED LANGUAGES
# ============================================================================
SUPPORTED_LANGUAGES = {
    'uz': {'name': '🇺🇿 O\'zbek', 'native': 'O\'zbek', 'flag': '🇺🇿'},
    'uz_cyrl': {'name': '🇺🇿 Ўзбек', 'native': 'Ўзбек', 'flag': '🇺🇿'},
    'ru': {'name': '🇷🇺 Русский', 'native': 'Русский', 'flag': '🇷🇺'},
    'en': {'name': '🇬🇧 English', 'native': 'English', 'flag': '🇬🇧'},
}

DEFAULT_LANGUAGE = 'en'  # Fallback language

# ============================================================================
# TRANSLATION KEYS (Complete Coverage)
# ============================================================================
TRANSLATIONS = {
    # ========== LANGUAGE SELECTION ==========
    'select_language': {
        'uz': '🌐 Tilni tanlang:',
        'uz_cyrl': '🌐 Тилни танланг:',
        'ru': '🌐 Выберите язык:',
        'en': '🌐 Select language:',
    },
    'language_changed': {
        'uz': '✅ Til o\'zgartirildi: {language}\n\nEndi barcha xabarlar {language} tilida bo\'ladi.',
        'uz_cyrl': '✅ Тил ўзгартирилди: {language}\n\nЭнди барча хабарлар {language} тилида бўлади.',
        'ru': '✅ Язык изменен: {language}\n\nТеперь все сообщения будут на {language}.',
        'en': '✅ Language changed: {language}\n\nAll messages will now be in {language}.',
    },
    
    # ========== WELCOME & ONBOARDING ==========
    'welcome': {
        'uz': '👋 Xush kelibsiz!\n\nBu bot sizga qiziqarli yangiliklarni yetkazib beradi.\n\n📱 Qiziqishlaringizni tanlang va yangiliklarni oling!',
        'uz_cyrl': '👋 Хуш келибсиз!\n\nБу бот сизга қизиқарли янгиликларни етказиб беради.\n\n📱 Қизиқишларингизни танланг ва янгиликларни олинг!',
        'ru': '👋 Добро пожаловать!\n\nЭтот бот доставляет вам интересные новости.\n\n📱 Выберите свои интересы и получайте новости!',
        'en': '👋 Welcome!\n\nThis bot delivers interesting news to you.\n\n📱 Choose your interests and get news!',
    },
    'trial_activated': {
        'uz': '🎉 Xush kelibsiz!\n\nSizga {days} kunlik bepul sinov berildi!\n\n📱 Endi qiziqishlaringizni tanlang va yangiliklarni oling!',
        'uz_cyrl': '🎉 Хуш келибсиз!\n\nСизга {days} кунлик бепул синов берилди!\n\n📱 Энди қизиқишларингизни танланг ва янгиликларни олинг!',
        'ru': '🎉 Добро пожаловать!\n\nВам предоставлен бесплатный пробный период на {days} дней!\n\n📱 Теперь выберите свои интересы и получайте новости!',
        'en': '🎉 Welcome!\n\nYou have been given a {days}-day free trial!\n\n📱 Now choose your interests and get news!',
    },
    
    # ========== PLANS & PRICING ==========
    'plans_header': {
        'uz': '💰 TARIFLAR',
        'uz_cyrl': '💰 ТАРИФЛАР',
        'ru': '💰 ТАРИФЫ',
        'en': '💰 PLANS',
    },
    'choose_plan': {
        'uz': 'Quyidagi tariflardan birini tanlang:',
        'uz_cyrl': 'Қуйидаги тарифлардан бирини танланг:',
        'ru': 'Выберите один из тарифов:',
        'en': 'Choose one of the plans:',
    },
    'plan_price': {
        'uz': '💰 Narx: {price:,} so\'m/oy',
        'uz_cyrl': '💰 Нарх: {price:,} сўм/ой',
        'ru': '💰 Цена: {price:,} сум/мес',
        'en': '💰 Price: {price:,} sum/month',
    },
    'plan_categories': {
        'uz': '📰 Kategoriyalar: {limit}',
        'uz_cyrl': '📰 Категориялар: {limit}',
        'ru': '📰 Категории: {limit}',
        'en': '📰 Categories: {limit}',
    },
    'plan_duration': {
        'uz': '⏰ Muddat: {days} kun',
        'uz_cyrl': '⏰ Муддат: {days} кун',
        'ru': '⏰ Срок: {days} дней',
        'en': '⏰ Duration: {days} days',
    },
    'unlimited': {
        'uz': 'Cheksiz',
        'uz_cyrl': 'Чексиз',
        'ru': 'Безлимит',
        'en': 'Unlimited',
    },
    'free_trial': {
        'uz': '🎁 Bepul sinov: {days} kun',
        'uz_cyrl': '🎁 Бепул синов: {days} кун',
        'ru': '🎁 Бесплатный пробный: {days} дней',
        'en': '🎁 Free trial: {days} days',
    },
    'all_categories': {
        'uz': '📰 Barcha kategoriyalar',
        'uz_cyrl': '📰 Барча категориялар',
        'ru': '📰 Все категории',
        'en': '📰 All categories',
    },
    'click_start': {
        'uz': 'Boshlash tugmasini bosing!',
        'uz_cyrl': 'Бошлаш тугмасини босинг!',
        'ru': 'Нажмите кнопку Начать!',
        'en': 'Click Start button!',
    },
    
    # ========== BUTTONS ==========
    'btn_start': {
        'uz': '🚀 Boshlash',
        'uz_cyrl': '🚀 Бошлаш',
        'ru': '🚀 Начать',
        'en': '🚀 Start',
    },
    'btn_interests': {
        'uz': '📋 Qiziqishlar',
        'uz_cyrl': '📋 Қизиқишлар',
        'ru': '📋 Интересы',
        'en': '📋 Interests',
    },
    'btn_status': {
        'uz': '📊 Status',
        'uz_cyrl': '📊 Статус',
        'ru': '📊 Статус',
        'en': '📊 Status',
    },
    'btn_help': {
        'uz': '❓ Yordam',
        'uz_cyrl': '❓ Ёрдам',
        'ru': '❓ Помощь',
        'en': '❓ Help',
    },
    'btn_language': {
        'uz': '🌐 Til',
        'uz_cyrl': '🌐 Тил',
        'ru': '🌐 Язык',
        'en': '🌐 Language',
    },
    'btn_plans': {
        'uz': '💰 Tariflar',
        'uz_cyrl': '💰 Тарифлар',
        'ru': '💰 Тарифы',
        'en': '💰 Plans',
    },
    'btn_statistics': {
        'uz': '📊 Statistika',
        'uz_cyrl': '📊 Статистика',
        'ru': '📊 Статистика',
        'en': '📊 Statistics',
    },
    'btn_admin_panel': {
        'uz': '🔐 Admin Panel',
        'uz_cyrl': '🔐 Админ Панел',
        'ru': '🔐 Админ Панель',
        'en': '🔐 Admin Panel',
    },
    'btn_view_plans': {
        'uz': '💳 Tariflarni ko\'rish',
        'uz_cyrl': '💳 Тарифларни кўриш',
        'ru': '💳 Посмотреть тарифы',
        'en': '💳 View plans',
    },
    'btn_back': {
        'uz': '◀️ Orqaga',
        'uz_cyrl': '◀️ Орқага',
        'ru': '◀️ Назад',
        'en': '◀️ Back',
    },
    'subscription_plans_header': {
        'uz': '💳 OBUNA TARIFLAR',
        'uz_cyrl': '💳 ОБУНА ТАРИФЛАР',
        'ru': '💳 ТАРИФЫ ПОДПИСКИ',
        'en': '💳 SUBSCRIPTION PLANS',
    },
    'which_plan': {
        'uz': 'Qaysi tarifni tanlamoqchisiz?',
        'uz_cyrl': 'Қайси тарифни танламоқчисиз?',
        'ru': 'Какой тариф вы хотите выбрать?',
        'en': 'Which plan would you like to choose?',
    },
    'current_plan': {
        'uz': '📌 Hozirgi tarifingiz',
        'uz_cyrl': '📌 Ҳозирги тарифингиз',
        'ru': '📌 Ваш текущий тариф',
        'en': '📌 Your current plan',
    },
    
    # ========== NEWS & CATEGORIES ==========
    'news_header': {
        'uz': '📰 YANGILIKLAR',
        'uz_cyrl': '📰 ЯНГИЛИКЛАР',
        'ru': '📰 НОВОСТИ',
        'en': '📰 NEWS',
    },
    'select_category': {
        'uz': 'Qaysi kategoriya bo\'yicha yangiliklar kerak?\n\n👇 Kategoriyani tanlang:',
        'uz_cyrl': 'Қайси категория бўйича янгиликлар керак?\n\n👇 Категорияни танланг:',
        'ru': 'По какой категории нужны новости?\n\n👇 Выберите категорию:',
        'en': 'Which category do you want news from?\n\n👇 Choose a category:',
    },
    'choose_plan_prompt': {
        'uz': '👇 Tarifni tanlang:',
        'uz_cyrl': '👇 Тарифни танланг:',
        'ru': '👇 Выберите тариф:',
        'en': '👇 Choose a plan:',
    },
    'category_selected': {
        'uz': '✅ Muvaffaqiyatli tanlandi!',
        'uz_cyrl': '✅ Муваффақиятли танланди!',
        'ru': '✅ Успешно выбрано!',
        'en': '✅ Successfully selected!',
    },
    'category_already_selected': {
        'uz': 'Bu kategoriya allaqachon tanlangan.',
        'uz_cyrl': 'Бу категория аллақачон танланган.',
        'ru': 'Эта категория уже выбрана.',
        'en': 'This category is already selected.',
    },
    'no_news_yet': {
        'uz': 'Hozircha bu kategoriyada yangiliklar yo\'q.\n\nYangiliklar kelishi bilan sizga avtomatik yuboriladi.',
        'uz_cyrl': 'Ҳозирча бу категорияда янгиликлар йўқ.\n\nЯнгиликлар келиши билан сизга автоматик юборилади.',
        'ru': 'Пока в этой категории нет новостей.\n\nКак только появятся новости, они будут автоматически отправлены вам.',
        'en': 'No news in this category yet.\n\nNews will be automatically sent to you as soon as they arrive.',
    },
    'latest_news': {
        'uz': '📰 Eng oxirgi yangilik:',
        'uz_cyrl': '📰 Энг охирги янгилик:',
        'ru': '📰 Последняя новость:',
        'en': '📰 Latest news:',
    },
    'other_categories': {
        'uz': '📰 Boshqa kategoriyalar uchun /interests',
        'uz_cyrl': '📰 Бошқа категориялар учун /interests',
        'ru': '📰 Для других категорий /interests',
        'en': '📰 For other categories /interests',
    },
    'video_too_large': {
        'uz': '🎥 Video: Juda katta (kanalda ko\'ring)',
        'uz_cyrl': '🎥 Видео: Жуда катта (каналда кўринг)',
        'ru': '🎥 Видео: Слишком большое (смотрите в канале)',
        'en': '🎥 Video: Too large (see in channel)',
    },
    
    # ========== CATEGORIES (Internal keys remain constant) ==========
    'cat_siyosat': {
        'uz': '🏛 Siyosat',
        'uz_cyrl': '🏛 Сиёсат',
        'ru': '🏛 Политика',
        'en': '🏛 Politics',
    },
    'cat_iqtisod': {
        'uz': '💰 Iqtisod',
        'uz_cyrl': '💰 Иқтисод',
        'ru': '💰 Экономика',
        'en': '💰 Economy',
    },
    'cat_jamiyat': {
        'uz': '👥 Jamiyat',
        'uz_cyrl': '👥 Жамият',
        'ru': '👥 Общество',
        'en': '👥 Society',
    },
    'cat_sport': {
        'uz': '⚽ Sport',
        'uz_cyrl': '⚽ Спорт',
        'ru': '⚽ Спорт',
        'en': '⚽ Sports',
    },
    'cat_texnologiya': {
        'uz': '💻 Texnologiya',
        'uz_cyrl': '💻 Технология',
        'ru': '💻 Технологии',
        'en': '💻 Technology',
    },
    'cat_dunyo': {
        'uz': '🌍 Dunyo',
        'uz_cyrl': '🌍 Дунё',
        'ru': '🌍 Мир',
        'en': '🌍 World',
    },
    'cat_salomatlik': {
        'uz': '🏥 Salomatlik',
        'uz_cyrl': '🏥 Саломатлик',
        'ru': '🏥 Здоровье',
        'en': '🏥 Health',
    },
    'cat_obhavo': {
        'uz': '🌤 Ob-havo',
        'uz_cyrl': '🌤 Об-ҳаво',
        'ru': '🌤 Погода',
        'en': '🌤 Weather',
    },
    
    # ========== STATUS & INFO ==========
    'status_header': {
        'uz': '📊 SIZNING STATUSINGIZ',
        'uz_cyrl': '📊 СИЗНИНГ СТАТУСИНГИЗ',
        'ru': '📊 ВАШ СТАТУС',
        'en': '📊 YOUR STATUS',
    },
    'status_username': {
        'uz': '👤 Username',
        'uz_cyrl': '👤 Username',
        'ru': '👤 Username',
        'en': '👤 Username',
    },
    'status_language': {
        'uz': '🌐 Til',
        'uz_cyrl': '🌐 Тил',
        'ru': '🌐 Язык',
        'en': '🌐 Language',
    },
    'status_plan': {
        'uz': '💳 Tarif',
        'uz_cyrl': '💳 Тариф',
        'ru': '💳 Тариф',
        'en': '💳 Plan',
    },
    'status_days_left': {
        'uz': '⏰ Qolgan kunlar',
        'uz_cyrl': '⏰ Қолган кунлар',
        'ru': '⏰ Осталось дней',
        'en': '⏰ Days left',
    },
    'status_interests': {
        'uz': '📋 Qiziqishlar',
        'uz_cyrl': '📋 Қизиқишлар',
        'ru': '📋 Интересы',
        'en': '📋 Interests',
    },
    'active': {
        'uz': 'Aktiv',
        'uz_cyrl': 'Актив',
        'ru': 'Активна',
        'en': 'Active',
    },
    'expired': {
        'uz': 'Tugagan',
        'uz_cyrl': 'Тугаган',
        'ru': 'Истекла',
        'en': 'Expired',
    },
    'trial': {
        'uz': 'Sinov',
        'uz_cyrl': 'Синов',
        'ru': 'Пробный',
        'en': 'Trial',
    },
    
    # ========== HELP ==========
    'help_text': {
        'uz': '❓ YORDAM\n\n'
              '📋 /interests — Qiziqishlarni boshqarish\n'
              '📊 /status — Sizning statusingiz\n'
              '🌐 /language — Tilni o\'zgartirish\n'
              '❓ /help — Yordam\n\n'
              '💡 Qiziqishlaringizni tanlang va yangiliklarni oling!\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '📞 Muammo bo\'lsa:\n\n'
              '👤 Admin: @Murodjon_PM',
        'uz_cyrl': '❓ ЁРДАМ\n\n'
                   '📋 /interests — Қизиқишларни бошқариш\n'
                   '📊 /status — Сизнинг статусингиз\n'
                   '🌐 /language — Тилни ўзгартириш\n'
                   '❓ /help — Ёрдам\n\n'
                   '💡 Қизиқишларингизни танланг ва янгиликларни олинг!\n\n'
                   '━━━━━━━━━━━━━━━━━━━━\n\n'
                   '📞 Муаммо бўлса:\n\n'
                   '👤 Админ: @Murodjon_PM',
        'ru': '❓ ПОМОЩЬ\n\n'
              '📋 /interests — Управление интересами\n'
              '📊 /status — Ваш статус\n'
              '🌐 /language — Изменить язык\n'
              '❓ /help — Помощь\n\n'
              '💡 Выберите свои интересы и получайте новости!\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '📞 Если возникли проблемы:\n\n'
              '👤 Админ: @Murodjon_PM',
        'en': '❓ HELP\n\n'
              '📋 /interests — Manage interests\n'
              '📊 /status — Your status\n'
              '🌐 /language — Change language\n'
              '❓ /help — Help\n\n'
              '💡 Select your interests and get news!\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '📞 If you have any issues:\n\n'
              '👤 Admin: @Murodjon_PM',
    },
    
    # ========== ERRORS ==========
    'error_generic': {
        'uz': '❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko\'ring.',
        'uz_cyrl': '❌ Хатолик юз берди. Илтимос, қайтадан уриниб кўринг.',
        'ru': '❌ Произошла ошибка. Пожалуйста, попробуйте снова.',
        'en': '❌ An error occurred. Please try again.',
    },
    'error_no_access': {
        'uz': '❌ Sizda bu funksiyaga kirish huquqi yo\'q.',
        'uz_cyrl': '❌ Сизда бу функцияга кириш ҳуқуқи йўқ.',
        'ru': '❌ У вас нет доступа к этой функции.',
        'en': '❌ You don\'t have access to this function.',
    },
    
    # ========== PAYMENT & SUBSCRIPTION ==========
    'price': {
        'uz': 'Narx',
        'uz_cyrl': 'Нарх',
        'ru': 'Цена',
        'en': 'Price',
    },
    'sum_month': {
        'uz': 'so\'m/oy',
        'uz_cyrl': 'сўм/ой',
        'ru': 'сум/мес',
        'en': 'sum/month',
    },
    'sum': {
        'uz': 'so\'m',
        'uz_cyrl': 'сўм',
        'ru': 'сум',
        'en': 'sum',
    },
    'duration': {
        'uz': 'Muddat',
        'uz_cyrl': 'Муддат',
        'ru': 'Срок',
        'en': 'Duration',
    },
    'creating_payment': {
        'uz': '⏳ To\'lov yaratilmoqda...',
        'uz_cyrl': '⏳ Тўлов яратилмоқда...',
        'ru': '⏳ Создание платежа...',
        'en': '⏳ Creating payment...',
    },
    'payment_created': {
        'uz': 'TO\'LOV YARATILDI',
        'uz_cyrl': 'ТЎЛОВ ЯРАТИЛДИ',
        'ru': 'ПЛАТЕЖ СОЗДАН',
        'en': 'PAYMENT CREATED',
    },
    'plan': {
        'uz': 'Tarif',
        'uz_cyrl': 'Тариф',
        'ru': 'Тариф',
        'en': 'Plan',
    },
    'amount': {
        'uz': 'Summa',
        'uz_cyrl': 'Сумма',
        'ru': 'Сумма',
        'en': 'Amount',
    },
    'transaction_id': {
        'uz': 'Tranzaksiya ID',
        'uz_cyrl': 'Транзакция ID',
        'ru': 'ID транзакции',
        'en': 'Transaction ID',
    },
    'click_to_pay': {
        'uz': 'To\'lovni amalga oshirish uchun tugmani bosing:',
        'uz_cyrl': 'Тўловни амалга ошириш учун тугмани босинг:',
        'ru': 'Нажмите кнопку для оплаты:',
        'en': 'Click the button to pay:',
    },
    'pay_now': {
        'uz': 'To\'lash',
        'uz_cyrl': 'Тўлаш',
        'ru': 'Оплатить',
        'en': 'Pay Now',
    },
    'check_payment': {
        'uz': 'Tekshirish',
        'uz_cyrl': 'Текшириш',
        'ru': 'Проверить',
        'en': 'Check Payment',
    },
    'checking_payment': {
        'uz': 'Tekshirilmoqda...',
        'uz_cyrl': 'Текширилмоқда...',
        'ru': 'Проверяется...',
        'en': 'Checking...',
    },
    'payment_success': {
        'uz': 'TO\'LOV MUVAFFAQIYATLI',
        'uz_cyrl': 'ТЎЛОВ МУВАФФАҚИЯТЛИ',
        'ru': 'ОПЛАТА УСПЕШНА',
        'en': 'PAYMENT SUCCESSFUL',
    },
    'valid_until': {
        'uz': 'Amal qilish muddati',
        'uz_cyrl': 'Амал қилиш муддати',
        'ru': 'Действует до',
        'en': 'Valid until',
    },
    'subscription_activated': {
        'uz': 'Obuna faollashtirildi! Endi barcha imkoniyatlardan foydalaning.',
        'uz_cyrl': 'Обуна фаоллаштирилди! Энди барча имкониятлардан фойдаланинг.',
        'ru': 'Подписка активирована! Теперь используйте все возможности.',
        'en': 'Subscription activated! Now use all features.',
    },
    'payment_pending': {
        'uz': 'To\'lov kutilmoqda',
        'uz_cyrl': 'Тўлов кутилмоқда',
        'ru': 'Ожидание оплаты',
        'en': 'Payment pending',
    },
    'complete_payment': {
        'uz': 'Iltimos, to\'lovni yakunlang.',
        'uz_cyrl': 'Илтимос, тўловни якунланг.',
        'ru': 'Пожалуйста, завершите оплату.',
        'en': 'Please complete the payment.',
    },
    'payment_failed': {
        'uz': 'To\'lov amalga oshmadi',
        'uz_cyrl': 'Тўлов амалга ошмади',
        'ru': 'Оплата не прошла',
        'en': 'Payment failed',
    },
    'payment_cancelled': {
        'uz': 'To\'lov bekor qilindi',
        'uz_cyrl': 'Тўлов бекор қилинди',
        'ru': 'Оплата отменена',
        'en': 'Payment cancelled',
    },
    'payment_unknown': {
        'uz': 'Noma\'lum status',
        'uz_cyrl': 'Номаълум статус',
        'ru': 'Неизвестный статус',
        'en': 'Unknown status',
    },
    'payment_error': {
        'uz': 'To\'lov yaratishda xato',
        'uz_cyrl': 'Тўлов яратишда хато',
        'ru': 'Ошибка создания платежа',
        'en': 'Payment creation error',
    },
    'try_again_later': {
        'uz': 'Keyinroq qayta urinib ko\'ring.',
        'uz_cyrl': 'Кейинроқ қайта уриниб кўринг.',
        'ru': 'Попробуйте позже.',
        'en': 'Please try again later.',
    },
    'try_again': {
        'uz': 'Qayta urinib ko\'ring.',
        'uz_cyrl': 'Қайта уриниб кўринг.',
        'ru': 'Попробуйте снова.',
        'en': 'Try again.',
    },
    'payment_not_found': {
        'uz': 'To\'lov topilmadi',
        'uz_cyrl': 'Тўлов топилмади',
        'ru': 'Платеж не найден',
        'en': 'Payment not found',
    },
    'check_error': {
        'uz': 'Tekshirishda xato',
        'uz_cyrl': 'Текширишда хато',
        'ru': 'Ошибка проверки',
        'en': 'Check error',
    },
}


# ============================================================================
# TRANSLATOR FUNCTION (Core of i18n system)
# ============================================================================
def t(key: str, lang: Optional[str] = None, **kwargs) -> str:
    """
    🌍 Universal translator function
    
    Args:
        key: Translation key (e.g., 'welcome', 'btn_start')
        lang: Language code (uz, uz_cyrl, ru, en). If None, uses DEFAULT_LANGUAGE
        **kwargs: Format parameters for string interpolation
    
    Returns:
        Translated text with fallback to English if translation missing
    
    Examples:
        >>> t('welcome', 'ru')
        '👋 Добро пожаловать!...'
        
        >>> t('plan_price', 'en', price=15000)
        '💰 Price: 15,000 sum/month'
    """
    # Validate language
    if lang is None or lang not in SUPPORTED_LANGUAGES:
        logger.warning(f"Invalid language '{lang}', falling back to {DEFAULT_LANGUAGE}")
        lang = DEFAULT_LANGUAGE
    
    # Get translation
    if key not in TRANSLATIONS:
        logger.error(f"Translation key '{key}' not found")
        return key  # Return key itself as fallback
    
    # Get text for language with fallback to English
    text = TRANSLATIONS[key].get(lang)
    if text is None:
        logger.warning(f"Translation for key '{key}' not found in '{lang}', using English")
        text = TRANSLATIONS[key].get(DEFAULT_LANGUAGE, key)
    
    # Apply string formatting if kwargs provided
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing format parameter {e} for key '{key}'")
            return text
    
    return text


def get_category_name(category_key: str, lang: str) -> str:
    """
    Get translated category name
    
    Args:
        category_key: Internal category key (siyosat, iqtisod, etc.)
        lang: Language code
    
    Returns:
        Translated category name with emoji
    """
    translation_key = f'cat_{category_key}'
    return t(translation_key, lang)


def get_language_name(lang_code: str, in_language: Optional[str] = None) -> str:
    """
    Get language name
    
    Args:
        lang_code: Language code to get name for
        in_language: Language to display name in (None = native name)
    
    Returns:
        Language name
    """
    if lang_code not in SUPPORTED_LANGUAGES:
        return lang_code
    
    if in_language is None:
        return SUPPORTED_LANGUAGES[lang_code]['native']
    
    return SUPPORTED_LANGUAGES[lang_code]['name']


def validate_language(lang: str) -> str:
    """
    Validate and normalize language code
    
    Args:
        lang: Language code to validate
    
    Returns:
        Valid language code or DEFAULT_LANGUAGE
    """
    if lang in SUPPORTED_LANGUAGES:
        return lang
    
    logger.warning(f"Invalid language code '{lang}', using default")
    return DEFAULT_LANGUAGE


# ============================================================================
# LANGUAGE-AWARE HELPERS
# ============================================================================
def format_number(number: int, lang: str) -> str:
    """Format number according to language locale"""
    # For now, simple comma formatting
    # Can be extended with locale-specific formatting
    return f"{number:,}"


def format_date(date, lang: str) -> str:
    """Format date according to language locale"""
    # Implement locale-specific date formatting
    # For now, simple ISO format
    return date.strftime('%Y-%m-%d')


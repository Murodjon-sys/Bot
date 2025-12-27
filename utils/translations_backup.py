"""
Ko'p tillilik uchun tarjimalar
"""

LANGUAGES = {
    'uz': '🇺🇿 O\'zbek',
    'uz_cyrl': '🇺🇿 Ўзбек',
    'ru': '🇷🇺 Русский',
    'en': '🇬🇧 English',
    'tr': '🇹🇷 Türkçe',
}

TRANSLATIONS = {
    # Til tanlash
    'select_language': {
        'uz': '🌐 Tilni tanlang:',
        'uz_cyrl': '🌐 Тилни танланг:',
        'ru': '🌐 Выберите язык:',
        'en': '🌐 Select language:'
    },
    'language_selected': {
        'uz': '✅ Til o\'zgartirildi: {language}',
        'uz_cyrl': '✅ Тил ўзгартирилди: {language}',
        'ru': '✅ Язык изменен: {language}',
        'en': '✅ Language changed: {language}'
    },
    
    # Bosh sahifa
    'welcome': {
        'uz': '👋 Xush kelibsiz!\n\nBu bot sizga qiziqarli yangiliklarni yetkazib beradi.\n\n📱 Qiziqishlaringizni tanlang va yangiliklarni oling!',
        'uz_cyrl': '👋 Хуш келибсиз!\n\nБу бот сизга қизиқарли янгиликларни етказиб беради.\n\n📱 Қизиқишларингизни танланг ва янгиликларни олинг!',
        'ru': '👋 Добро пожаловать!\n\nЭтот бот доставляет вам интересные новости.\n\n📱 Выберите свои интересы и получайте новости!',
        'en': '👋 Welcome!\n\nThis bot delivers interesting news to you.\n\n📱 Choose your interests and get news!'
    },
    'select_interests': {
        'uz': '📋 Qiziqishlaringizni tanlang:',
        'uz_cyrl': '📋 Қизиқишларингизни танланг:',
        'ru': '📋 Выберите свои интересы:',
        'en': '📋 Select your interests:'
    },
    
    # Kategoriyalar
    'categories': {
        'siyosat': {
            'uz': '🏛 Siyosat',
            'uz_cyrl': '🏛 Сиёсат',
            'ru': '🏛 Политика',
            'en': '🏛 Politics'
        },
        'iqtisod': {
            'uz': '💰 Iqtisod',
            'uz_cyrl': '💰 Иқтисод',
            'ru': '💰 Экономика',
            'en': '💰 Economy'
        },
        'jamiyat': {
            'uz': '👥 Jamiyat',
            'uz_cyrl': '👥 Жамият',
            'ru': '👥 Общество',
            'en': '👥 Society'
        },
        'sport': {
            'uz': '⚽ Sport',
            'uz_cyrl': '⚽ Спорт',
            'ru': '⚽ Спорт',
            'en': '⚽ Sports'
        },
        'texnologiya': {
            'uz': '💻 Texnologiya',
            'uz_cyrl': '💻 Технология',
            'ru': '💻 Технологии',
            'en': '💻 Technology'
        },
        'dunyo': {
            'uz': '🌍 Dunyo',
            'uz_cyrl': '🌍 Дунё',
            'ru': '🌍 Мир',
            'en': '🌍 World'
        },
        'salomatlik': {
            'uz': '🏥 Salomatlik',
            'uz_cyrl': '🏥 Саломатлик',
            'ru': '🏥 Здоровье',
            'en': '🏥 Health'
        },
        'obhavo': {
            'uz': '🌤 Ob-havo',
            'uz_cyrl': '🌤 Об-ҳаво',
            'ru': '🌤 Погода',
            'en': '🌤 Weather'
        }
    },
    
    # Tugmalar
    'btn_interests': {
        'uz': '📋 Qiziqishlar',
        'uz_cyrl': '📋 Қизиқишлар',
        'ru': '📋 Интересы',
        'en': '📋 Interests'
    },
    'btn_status': {
        'uz': '📊 Status',
        'uz_cyrl': '📊 Статус',
        'ru': '📊 Статус',
        'en': '📊 Status'
    },
    'btn_help': {
        'uz': '❓ Yordam',
        'uz_cyrl': '❓ Ёрдам',
        'ru': '❓ Помощь',
        'en': '❓ Help'
    },
    'btn_language': {
        'uz': '🌐 Til',
        'uz_cyrl': '🌐 Тил',
        'ru': '🌐 Язык',
        'en': '🌐 Language'
    },
    
    # Qiziqishlar
    'category_added': {
        'uz': '✅ {category} qo\'shildi',
        'uz_cyrl': '✅ {category} қўшилди',
        'ru': '✅ {category} добавлена',
        'en': '✅ {category} added'
    },
    'category_removed': {
        'uz': '❌ {category} o\'chirildi',
        'uz_cyrl': '❌ {category} ўчирилди',
        'ru': '❌ {category} удалена',
        'en': '❌ {category} removed'
    },
    'category_already_selected': {
        'uz': 'Bu kategoriya allaqachon tanlangan.',
        'uz_cyrl': 'Бу категория аллақачон танланган.',
        'ru': 'Эта категория уже выбрана.',
        'en': 'This category is already selected.'
    },
    
    # Status
    'status_info': {
        'uz': '📊 **Sizning statusingiz:**\n\n'
              '👤 Username: @{username}\n'
              '📅 Ro\'yxatdan o\'tgan: {created}\n'
              '🎯 Tanlangan kategoriyalar: {categories}\n\n'
              '⏰ Trial: {trial}\n'
              '💳 Obuna: {subscription}',
        'uz_cyrl': '📊 **Сизнинг статусингиз:**\n\n'
                   '👤 Username: @{username}\n'
                   '📅 Рўйхатдан ўтган: {created}\n'
                   '🎯 Танланган категориялар: {categories}\n\n'
                   '⏰ Trial: {trial}\n'
                   '💳 Обуна: {subscription}',
        'ru': '📊 **Ваш статус:**\n\n'
              '👤 Username: @{username}\n'
              '📅 Зарегистрирован: {created}\n'
              '🎯 Выбранные категории: {categories}\n\n'
              '⏰ Пробный период: {trial}\n'
              '💳 Подписка: {subscription}',
        'en': '📊 **Your status:**\n\n'
              '👤 Username: @{username}\n'
              '📅 Registered: {created}\n'
              '🎯 Selected categories: {categories}\n\n'
              '⏰ Trial: {trial}\n'
              '💳 Subscription: {subscription}'
    },
    'active': {
        'uz': 'Aktiv',
        'uz_cyrl': 'Актив',
        'ru': 'Активна',
        'en': 'Active'
    },
    'expired': {
        'uz': 'Tugagan',
        'uz_cyrl': 'Тугаган',
        'ru': 'Истекла',
        'en': 'Expired'
    },
    'not_active': {
        'uz': 'Yo\'q',
        'uz_cyrl': 'Йўқ',
        'ru': 'Нет',
        'en': 'No'
    },
    
    # Yordam
    'help_text': {
        'uz': '❓ **Yordam**\n\n'
              '📋 /interests — Qiziqishlarni boshqarish\n'
              '📊 /status — Sizning statusingiz\n'
              '🌐 /language — Tilni o\'zgartirish\n'
              '❓ /help — Yordam\n\n'
              '💡 Qiziqishlaringizni tanlang va yangiliklarni oling!',
        'uz_cyrl': '❓ **Ёрдам**\n\n'
                   '📋 /interests — Қизиқишларни бошқариш\n'
                   '📊 /status — Сизнинг статусингиз\n'
                   '🌐 /language — Тилни ўзгартириш\n'
                   '❓ /help — Ёрдам\n\n'
                   '💡 Қизиқишларингизни танланг ва янгиликларни олинг!',
        'ru': '❓ **Помощь**\n\n'
              '📋 /interests — Управление интересами\n'
              '📊 /status — Ваш статус\n'
              '🌐 /language — Изменить язык\n'
              '❓ /help — Помощь\n\n'
              '💡 Выберите свои интересы и получайте новости!',
        'en': '❓ **Help**\n\n'
              '📋 /interests — Manage interests\n'
              '📊 /status — Your status\n'
              '🌐 /language — Change language\n'
              '❓ /help — Help\n\n'
              '💡 Select your interests and get news!'
    },
    
    # Yangiliklar
    'latest_news': {
        'uz': '📰 Eng oxirgi yangilik:',
        'uz_cyrl': '📰 Энг охирги янгилик:',
        'ru': '📰 Последняя новость:',
        'en': '📰 Latest news:'
    },
    'other_categories': {
        'uz': '📰 Boshqa kategoriyalar uchun /interests',
        'uz_cyrl': '📰 Бошқа категориялар учун /interests',
        'ru': '📰 Для других категорий /interests',
        'en': '📰 For other categories /interests'
    }
}

def get_text(key: str, lang: str = 'uz', **kwargs) -> str:
    """
    Tarjima olish
    
    Args:
        key: Tarjima kaliti
        lang: Til kodi (uz, uz_cyrl, ru, en)
        **kwargs: Format parametrlari
    
    Returns:
        Tarjima qilingan matn
    """
    if key not in TRANSLATIONS:
        return key
    
    text = TRANSLATIONS[key].get(lang, TRANSLATIONS[key].get('uz', key))
    
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    
    return text

def get_category_name(category: str, lang: str = 'uz') -> str:
    """
    Kategoriya nomini olish
    
    Args:
        category: Kategoriya kodi
        lang: Til kodi
    
    Returns:
        Tarjima qilingan kategoriya nomi
    """
    if category not in TRANSLATIONS['categories']:
        return category
    
    return TRANSLATIONS['categories'][category].get(lang, category)

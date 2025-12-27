"""
🌍 Multilingual Translation System (Backward Compatible)
This module provides backward compatibility with old translation system
while using the new i18n architecture
"""

# Import new system
from utils.i18n import (
    t,
    get_category_name as _get_category_name,
    SUPPORTED_LANGUAGES,
    DEFAULT_LANGUAGE,
    validate_language
)

# Backward compatibility: Export LANGUAGES in old format
LANGUAGES = {
    'uz': "O'zbek (Lotin)",
    'uz_cyrl': 'Ўзбек (Кирилл)',
    'ru': 'Русский',
    'en': 'English',
}

# Old TRANSLATIONS structure (for backward compatibility)
# Now redirects to new i18n system
TRANSLATIONS = {
    'select_language': {
        'uz': '🌐 Tilni tanlang:',
        'uz_cyrl': '🌐 Тилни танланг:',
        'ru': '🌐 Выберите язык:',
        'en': '🌐 Select language:',
    },
    'select_interests': {
        'uz': '📋 Qiziqishlaringizni tanlang:',
        'uz_cyrl': '📋 Қизиқишларингизни танланг:',
        'ru': '📋 Выберите свои интересы:',
        'en': '📋 Select your interests:',
    },
    'btn_interests': {
        'uz': '📋 Qiziqishlar',
        'uz_cyrl': '📋 Қизиқишлар',
        'ru': '📋 Интересы',
        'en': '📋 Interests',
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
    'help_text': {
        'uz': '❓ **YORDAM**\n\n'
              '📋 /interests — Qiziqishlarni boshqarish\n'
              '📊 /status — Sizning statusingiz\n'
              '🌐 /language — Tilni o\'zgartirish\n'
              '❓ /help — Yordam\n\n'
              '💡 Qiziqishlaringizni tanlang va yangiliklarni oling!\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '📞 **Muammo bo\'lsa:**\n'
              '👤 Admin: @Murodjon_PM',
        'uz_cyrl': '❓ **ЁРДАМ**\n\n'
                   '📋 /interests — Қизиқишларни бошқариш\n'
                   '📊 /status — Сизнинг статусингиз\n'
                   '🌐 /language — Тилни ўзгартириш\n'
                   '❓ /help — Ёрдам\n\n'
                   '💡 Қизиқишларингизни танланг ва янгиликларни олинг!\n\n'
                   '━━━━━━━━━━━━━━━━━━━━\n\n'
                   '📞 **Муаммо бўлса:**\n'
                   '👤 Админ: @Murodjon_PM',
        'ru': '❓ **ПОМОЩЬ**\n\n'
              '📋 /interests — Управление интересами\n'
              '📊 /status — Ваш статус\n'
              '🌐 /language — Изменить язык\n'
              '❓ /help — Помощь\n\n'
              '💡 Выберите свои интересы и получайте новости!\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '📞 **Если возникли проблемы:**\n'
              '👤 Админ: @Murodjon_PM',
        'en': '❓ **HELP**\n\n'
              '📋 /interests — Manage interests\n'
              '📊 /status — Your status\n'
              '🌐 /language — Change language\n'
              '❓ /help — Help\n\n'
              '💡 Select your interests and get news!\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '📞 **If you have any issues:**\n'
              '👤 Admin: @Murodjon_PM',
    },
    'categories': {
        'siyosat': {
            'uz': '🏛 Siyosat',
            'uz_cyrl': '🏛 Сиёсат',
            'ru': '🏛 Политика',
            'en': '🏛 Politics',
        },
        'iqtisod': {
            'uz': '💰 Iqtisod',
            'uz_cyrl': '💰 Иқтисод',
            'ru': '💰 Экономика',
            'en': '💰 Economy',
        },
        'jamiyat': {
            'uz': '👥 Jamiyat',
            'uz_cyrl': '👥 Жамият',
            'ru': '👥 Общество',
            'en': '👥 Society',
        },
        'sport': {
            'uz': '⚽ Sport',
            'uz_cyrl': '⚽ Спорт',
            'ru': '⚽ Спорт',
            'en': '⚽ Sports',
        },
        'texnologiya': {
            'uz': '💻 Texnologiya',
            'uz_cyrl': '💻 Технология',
            'ru': '💻 Технологии',
            'en': '💻 Technology',
        },
        'dunyo': {
            'uz': '🌍 Dunyo',
            'uz_cyrl': '🌍 Дунё',
            'ru': '🌍 Мир',
            'en': '🌍 World',
        },
        'salomatlik': {
            'uz': '🏥 Salomatlik',
            'uz_cyrl': '🏥 Саломатлик',
            'ru': '🏥 Здоровье',
            'en': '🏥 Health',
        },
        'obhavo': {
            'uz': '🌤 Ob-havo',
            'uz_cyrl': '🌤 Об-ҳаво',
            'ru': '🌤 Погода',
            'en': '🌤 Weather',
        },
    },
}


def get_text(key: str, lang: str = 'uz', **kwargs) -> str:
    """
    Backward compatible translation function
    Redirects to new i18n system
    
    Args:
        key: Translation key
        lang: Language code
        **kwargs: Format parameters
    
    Returns:
        Translated text
    """
    # Map old keys to new keys
    key_mapping = {
        'select_interests': 'select_category',
        'btn_interests': 'btn_interests',
        'btn_help': 'btn_help',
        'btn_language': 'btn_language',
        'help_text': 'help_text',
    }
    
    # Use mapped key if exists, otherwise use original
    new_key = key_mapping.get(key, key)
    
    # Call new translation system
    return t(new_key, lang, **kwargs)


def get_category_name(category: str, lang: str = 'uz') -> str:
    """
    Backward compatible category name function
    Redirects to new i18n system
    
    Args:
        category: Category key (siyosat, iqtisod, etc.)
        lang: Language code
    
    Returns:
        Translated category name
    """
    return _get_category_name(category, lang)

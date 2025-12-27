# 🌍 Production-Ready Multilingual Architecture

## 📋 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Core Principles](#core-principles)
3. [Implementation Guide](#implementation-guide)
4. [Code Examples](#code-examples)
5. [Best Practices](#best-practices)
6. [Testing Strategy](#testing-strategy)

---

## 🏗️ Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERACTION                         │
│  (Telegram Bot - Any Language: uz, uz_cyrl, ru, en)         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              LANGUAGE DETECTION LAYER                        │
│  • Load user.language from database                          │
│  • Validate language code                                    │
│  • Fallback to English if invalid                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              TRANSLATION LAYER (i18n)                        │
│  • t(key, lang, **kwargs) - Universal translator            │
│  • Centralized TRANSLATIONS dictionary                       │
│  • Automatic fallback: lang → English → key                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              CONTENT DELIVERY                                │
│  • UI Text: Always translated                                │
│  • Buttons: Always translated                                │
│  • News: Auto-translated if not in user language            │
│  • Errors: Always translated                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Core Principles

### 1. **Single Source of Truth**
- All translations in `utils/i18n.py`
- NO hardcoded text anywhere in bot code
- Internal keys remain constant (e.g., `siyosat`, `iqtisod`)

### 2. **Language Persistence**
```python
# Database schema
class User:
    telegram_id: int
    language: str  # 'uz', 'uz_cyrl', 'ru', 'en'
    # ... other fields
```

### 3. **Universal Translator Function**
```python
from utils.i18n import t

# Simple usage
text = t('welcome', user.language)

# With parameters
text = t('plan_price', user.language, price=15000)
# Output (ru): "💰 Цена: 15,000 сум/мес"
```

### 4. **Fallback Chain**
```
User Language → English → Translation Key
```

### 5. **Language-Independent Callbacks**
```python
# ✅ CORRECT: Language-independent
callback_data = "select_category_siyosat"

# ❌ WRONG: Language-dependent
callback_data = "select_category_Политика"
```

---

## 🛠️ Implementation Guide

### Step 1: Update Database Model

```python
# db/models.py
from sqlalchemy import Column, String

class User(Base):
    __tablename__ = 'users'
    
    telegram_id = Column(BigInteger, primary_key=True)
    language = Column(String(10), default='en')  # uz, uz_cyrl, ru, en
    # ... other fields
```

### Step 2: Create Language Middleware

```python
# bot/middleware.py
from utils.i18n import validate_language

async def get_user_language(telegram_id: int) -> str:
    """
    Get user's language from database
    Always call this before sending any message
    """
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if user and user.language:
            return validate_language(user.language)
        
        return 'en'  # Default for new users
```

### Step 3: Update All Handlers

#### ❌ BEFORE (Hardcoded):
```python
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Xush kelibsiz!\n\nBu bot sizga yangiliklarni yetkazib beradi."
    )
```

#### ✅ AFTER (Multilingual):
```python
from utils.i18n import t
from bot.middleware import get_user_language

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = await get_user_language(update.effective_user.id)
    
    await update.message.reply_text(
        t('welcome', lang),
        parse_mode='Markdown'
    )
```

### Step 4: Multilingual Keyboards

#### ❌ BEFORE (Hardcoded):
```python
keyboard = [
    [InlineKeyboardButton("🏛 Siyosat", callback_data="cat_siyosat")],
    [InlineKeyboardButton("💰 Iqtisod", callback_data="cat_iqtisod")],
]
```

#### ✅ AFTER (Multilingual):
```python
from utils.i18n import t, get_category_name

async def get_categories_keyboard(lang: str):
    categories = ['siyosat', 'iqtisod', 'jamiyat', 'sport', 
                  'texnologiya', 'dunyo', 'salomatlik', 'obhavo']
    
    keyboard = []
    for category in categories:
        # Display name is translated, callback_data is constant
        button_text = get_category_name(category, lang)
        keyboard.append([
            InlineKeyboardButton(
                button_text, 
                callback_data=f"cat_{category}"  # Language-independent!
            )
        ])
    
    return InlineKeyboardMarkup(keyboard)
```

### Step 5: News Translation

```python
# bot/bot.py
async def send_news_to_user(self, telegram_id: int, news_text: str, 
                            category: str, lang: str):
    """
    Send news to user in their language
    """
    from services.translator import translate_text
    from utils.i18n import t, get_category_name
    
    # Translate category name
    category_name = get_category_name(category, lang)
    
    # Translate news content
    try:
        translated_news = await translate_text(news_text, lang)
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        translated_news = news_text  # Fallback to original
    
    # Translate footer
    footer = t('other_categories', lang)
    
    # Compose message
    message = f"{category_name}\n\n{translated_news}\n\n━━━━━━━━━━━━━━━━━━━━\n\n{footer}"
    
    await self.app.bot.send_message(
        chat_id=telegram_id,
        text=message,
        parse_mode='Markdown'
    )
```

---

## 💻 Code Examples

### Example 1: Language Selection

```python
# bot/language_handler.py
from utils.i18n import t, SUPPORTED_LANGUAGES

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show language selection menu"""
    telegram_id = update.effective_user.id
    current_lang = await get_user_language(telegram_id)
    
    # Create keyboard with all supported languages
    keyboard = []
    for lang_code, lang_info in SUPPORTED_LANGUAGES.items():
        keyboard.append([
            InlineKeyboardButton(
                lang_info['name'],
                callback_data=f"set_lang_{lang_code}"
            )
        ])
    
    await update.message.reply_text(
        t('select_language', current_lang),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("set_lang_"):
        new_lang = query.data.replace("set_lang_", "")
        telegram_id = update.effective_user.id
        
        # Update database
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                user.language = new_lang
                await session.commit()
                
                # Confirm in NEW language
                lang_name = SUPPORTED_LANGUAGES[new_lang]['native']
                await query.edit_message_text(
                    t('language_changed', new_lang, language=lang_name),
                    parse_mode='Markdown'
                )
```

### Example 2: Status Command

```python
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user status in their language"""
    telegram_id = update.effective_user.id
    lang = await get_user_language(telegram_id)
    
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await update.message.reply_text(t('error_generic', lang))
            return
        
        # Build status message
        status_text = f"┌ {t('status_header', lang)}\n"
        status_text += f"├ {t('status_username', lang)}: @{user.username or 'N/A'}\n"
        status_text += f"├ {t('status_language', lang)}: {SUPPORTED_LANGUAGES[lang]['native']}\n"
        
        # Plan status
        if user.subscription_end and user.subscription_end > datetime.utcnow():
            days_left = (user.subscription_end - datetime.utcnow()).days
            plan_status = f"{user.subscription_plan} ({days_left} {t('status_days_left', lang).lower()})"
        else:
            plan_status = t('expired', lang)
        
        status_text += f"├ {t('status_plan', lang)}: {plan_status}\n"
        status_text += f"└ {t('status_interests', lang)}: {len(user.interests)}\n"
        
        await update.message.reply_text(status_text)
```

### Example 3: Error Handling

```python
async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global error handler - always in user's language"""
    try:
        telegram_id = update.effective_user.id
        lang = await get_user_language(telegram_id)
    except:
        lang = 'en'  # Fallback if can't get user language
    
    error_message = t('error_generic', lang)
    
    try:
        await update.message.reply_text(error_message)
    except:
        # If can't send message, log it
        logger.error(f"Failed to send error message to {telegram_id}")
```

---

## ✅ Best Practices

### 1. **Always Load User Language First**
```python
# ✅ CORRECT
async def any_handler(update, context):
    lang = await get_user_language(update.effective_user.id)
    text = t('some_key', lang)
    await update.message.reply_text(text)

# ❌ WRONG
async def any_handler(update, context):
    await update.message.reply_text("Hardcoded text")
```

### 2. **Use Language-Independent Callback Data**
```python
# ✅ CORRECT
callback_data = "action_category_siyosat"

# ❌ WRONG
callback_data = f"action_category_{t('cat_siyosat', lang)}"
```

### 3. **Validate All Language Codes**
```python
from utils.i18n import validate_language

user_lang = validate_language(user.language)  # Always safe
```

### 4. **Test All Languages**
```python
# Test script
from utils.i18n import t, SUPPORTED_LANGUAGES

for lang in SUPPORTED_LANGUAGES:
    print(f"\n=== Testing {lang} ===")
    print(t('welcome', lang))
    print(t('btn_start', lang))
    # ... test all keys
```

### 5. **Handle Missing Translations Gracefully**
```python
# The t() function automatically falls back to English
# No need for try-except in most cases
text = t('some_key', user_lang)  # Safe, will never crash
```

---

## 🧪 Testing Strategy

### Unit Tests

```python
# tests/test_i18n.py
import pytest
from utils.i18n import t, validate_language, get_category_name

def test_translation_exists():
    """Test that all keys have translations in all languages"""
    from utils.i18n import TRANSLATIONS, SUPPORTED_LANGUAGES
    
    for key in TRANSLATIONS:
        for lang in SUPPORTED_LANGUAGES:
            assert lang in TRANSLATIONS[key], f"Missing {lang} for {key}"

def test_fallback_to_english():
    """Test fallback mechanism"""
    # Non-existent language should fallback to English
    text = t('welcome', 'invalid_lang')
    assert text == TRANSLATIONS['welcome']['en']

def test_category_translation():
    """Test category name translation"""
    for lang in ['uz', 'uz_cyrl', 'ru', 'en']:
        name = get_category_name('siyosat', lang)
        assert name  # Should not be empty
        assert '🏛' in name  # Should have emoji

def test_string_formatting():
    """Test parameter substitution"""
    text = t('plan_price', 'en', price=15000)
    assert '15,000' in text
```

### Integration Tests

```python
# tests/test_multilingual_flow.py
async def test_language_switch_flow():
    """Test complete language switching flow"""
    # 1. User starts bot (default English)
    # 2. User selects Russian
    # 3. All subsequent messages should be in Russian
    # 4. User switches to Uzbek
    # 5. All messages now in Uzbek
    pass  # Implement with pytest-asyncio
```

---

## 🚀 Migration Checklist

- [ ] Create `utils/i18n.py` with all translations
- [ ] Add `language` column to User model
- [ ] Create `get_user_language()` middleware
- [ ] Update all handlers to use `t()` function
- [ ] Update all keyboards to be multilingual
- [ ] Implement news translation
- [ ] Add language selection command
- [ ] Test all languages
- [ ] Add error handling in user's language
- [ ] Update admin panel (if needed)
- [ ] Deploy and monitor

---

## 📚 Additional Resources

### Adding New Language

1. Add to `SUPPORTED_LANGUAGES` in `utils/i18n.py`
2. Add translations for ALL keys in `TRANSLATIONS`
3. Test thoroughly
4. Deploy

### Adding New Translation Key

1. Add key to `TRANSLATIONS` with all languages
2. Use `t('new_key', lang)` in code
3. Test in all languages

---

## 🎯 Success Criteria

✅ User selects language → ALL text switches immediately
✅ No hardcoded text anywhere in bot
✅ News content translated to user language
✅ Buttons and menus in user language
✅ Error messages in user language
✅ Easy to add new languages
✅ Fallback mechanism works correctly
✅ No mixed languages ever shown to user

---

**Remember:** The key to successful multilingual bot is **consistency**. Every single text output must go through the translation system. No exceptions!

# 🚀 PARSE_MODE QUICK REFERENCE

## ⚡ Quick Start

```python
from utils.telegram_formatter import (
    build_news_message,
    send_safe_message,
    escape_html
)

# 1. Build message
message = build_news_message(
    category_name="🏛 Politics",
    news_content=news_text,
    footer="📰 Other categories",
    escape_content=True  # ← CRITICAL!
)

# 2. Send safely
await send_safe_message(
    bot=bot,
    chat_id=user_id,
    text=message,
    parse_mode="HTML",
    fallback_to_plain=True
)
```

## 🛡️ Golden Rules

### ✅ DO:
- Use **HTML** (not Markdown)
- **Escape ALL** external content
- Use `send_safe_message()` with fallback
- Use message templates
- Test with multilingual content

### ❌ DON'T:
- Use Markdown/MarkdownV2
- Trust external content
- Ignore parse errors
- Mix escaped/unescaped content
- Skip testing

## 📝 Common Patterns

### Escape External Content
```python
# ALWAYS escape:
news = escape_html(channel_message)
translated = escape_html(translated_text)
user_input = escape_html(user.message)
```

### Format Text
```python
from utils.telegram_formatter import format_bold, format_italic

bold = format_bold("Important", escape=True)
italic = format_italic("Note", escape=True)
```

### Build Messages
```python
# News
message = build_news_message(
    category_name=category,
    news_content=news,
    footer=footer,
    escape_content=True
)

# Status
message = build_status_message(
    header="👤 PROFILE",
    fields={"Username": "@user", "Plan": "Premium"},
    escape_values=True
)

# Error
message = build_error_message(
    error_title="❌ ERROR",
    error_description="Something went wrong",
    escape=True
)
```

### Send Messages
```python
# Safe send (recommended)
await send_safe_message(
    bot=bot,
    chat_id=chat_id,
    text=message,
    parse_mode="HTML",
    fallback_to_plain=True
)

# With media
await bot.send_photo(
    chat_id=chat_id,
    photo=photo,
    caption=message,
    parse_mode="HTML"
)
```

## 🔍 Debugging

### Validate HTML
```python
from utils.telegram_formatter import validate_html

is_valid, error = validate_html(message)
if not is_valid:
    print(f"Invalid: {error}")
```

### Debug Errors
```python
from utils.telegram_formatter import debug_parse_error

try:
    await bot.send_message(...)
except Exception as e:
    print(debug_parse_error(message, e))
```

## 🧪 Testing

```bash
# Run tests
python test_telegram_formatter.py

# Should see:
# 🎉 ALL TESTS PASSED! 🎉
```

## ⚠️ Common Mistakes

```python
# ❌ WRONG
message = f"<b>{news_from_channel}</b>"  # Not escaped!
parse_mode='Markdown'  # Use HTML!

# ✅ CORRECT
news_safe = escape_html(news_from_channel)
message = f"<b>{news_safe}</b>"
parse_mode='HTML'
```

## 📊 HTML vs Markdown

| Feature | HTML | Markdown |
|---------|------|----------|
| Special chars | 5 (`< > & " '`) | 18+ |
| Escaping | Simple | Complex |
| Multilingual | ✅ Excellent | ⚠️ Issues |
| Debugging | ✅ Easy | ❌ Hard |
| **Recommended** | ✅ **YES** | ❌ NO |

## 🎯 Production Checklist

- [ ] Using HTML (not Markdown)
- [ ] All external content escaped
- [ ] Using `send_safe_message()`
- [ ] Fallback enabled
- [ ] Tests passing
- [ ] Error logging configured
- [ ] Tested with real data
- [ ] Tested multilingual content

## 📚 Full Documentation

See `PARSE_MODE_FIX_GUIDE.md` for complete guide.

---

**Remember:** Always escape external content! 🛡️

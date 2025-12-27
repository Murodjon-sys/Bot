# 🔄 MIGRATION EXAMPLES - Before & After

## Example 1: Simple Message

### ❌ Before (Unsafe)
```python
async def send_welcome(update, context):
    await update.message.reply_text(
        f"**Welcome {user.name}!**\n\nYour plan: {user.plan}",
        parse_mode='Markdown'
    )
```

### ✅ After (Safe)
```python
from utils.telegram_formatter import format_bold, escape_html, send_safe_message

async def send_welcome(update, context):
    # Escape user data
    safe_name = escape_html(user.name)
    safe_plan = escape_html(user.plan)
    
    # Build message
    message = f"{format_bold('Welcome ' + safe_name, escape=False)}!\n\nYour plan: {safe_plan}"
    
    # Send safely
    await send_safe_message(
        bot=context.bot,
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode="HTML",
        fallback_to_plain=True
    )
```

## Example 2: News Message

### ❌ Before (Unsafe)
```python
async def send_news(bot, user_id, news_text, category):
    message = f"**{category}**\n\n{news_text}\n\n📰 More news: /interests"
    
    await bot.send_message(
        chat_id=user_id,
        text=message,
        parse_mode='Markdown'
    )
```

### ✅ After (Safe)
```python
from utils.telegram_formatter import build_news_message, send_safe_message

async def send_news(bot, user_id, news_text, category):
    # Build safe message (auto-escapes)
    message = build_news_message(
        category_name=category,
        news_content=news_text,
        footer="📰 More news: /interests",
        escape_content=True  # CRITICAL!
    )
    
    # Send safely with fallback
    await send_safe_message(
        bot=bot,
        chat_id=user_id,
        text=message,
        parse_mode="HTML",
        fallback_to_plain=True
    )
```

## Example 3: Status Message

### ❌ Before (Unsafe)
```python
async def show_status(update, context):
    status = f"""
**YOUR STATUS**

Username: @{user.username}
Plan: {user.plan}
Days left: {user.days_left}
"""
    
    await update.message.reply_text(status, parse_mode='Markdown')
```

### ✅ After (Safe)
```python
from utils.telegram_formatter import build_status_message, send_safe_message

async def show_status(update, context):
    # Build safe status message
    message = build_status_message(
        header="YOUR STATUS",
        fields={
            "Username": f"@{user.username}",
            "Plan": user.plan,
            "Days left": str(user.days_left)
        },
        escape_values=True  # Auto-escape all values
    )
    
    # Send safely
    await send_safe_message(
        bot=context.bot,
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode="HTML",
        fallback_to_plain=True
    )
```

## Example 4: Error Message

### ❌ Before (Unsafe)
```python
async def handle_error(update, context, error_msg):
    await update.message.reply_text(
        f"**ERROR**\n\n{error_msg}",
        parse_mode='Markdown'
    )
```

### ✅ After (Safe)
```python
from utils.telegram_formatter import build_error_message, send_safe_message

async def handle_error(update, context, error_msg):
    # Build safe error message
    message = build_error_message(
        error_title="❌ ERROR",
        error_description=error_msg,
        escape=True  # Escape error message
    )
    
    # Send safely
    await send_safe_message(
        bot=context.bot,
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode="HTML",
        fallback_to_plain=True
    )
```

## Example 5: Message with Link

### ❌ Before (Unsafe)
```python
async def send_article(update, context, title, url):
    message = f"**{title}**\n\n[Read more]({url})"
    
    await update.message.reply_text(message, parse_mode='Markdown')
```

### ✅ After (Safe)
```python
from utils.telegram_formatter import format_bold, format_link, escape_html, send_safe_message

async def send_article(update, context, title, url):
    # Escape title
    safe_title = escape_html(title)
    
    # Build message
    message = f"{format_bold(safe_title, escape=False)}\n\n{format_link('Read more', url)}"
    
    # Send safely
    await send_safe_message(
        bot=context.bot,
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode="HTML",
        fallback_to_plain=True
    )
```

## Example 6: Message with Media

### ❌ Before (Unsafe)
```python
async def send_photo_with_caption(bot, user_id, photo, caption):
    await bot.send_photo(
        chat_id=user_id,
        photo=photo,
        caption=f"**News**\n\n{caption}",
        parse_mode='Markdown'
    )
```

### ✅ After (Safe)
```python
from utils.telegram_formatter import format_bold, escape_html

async def send_photo_with_caption(bot, user_id, photo, caption):
    # Escape caption
    safe_caption = escape_html(caption)
    
    # Build caption
    full_caption = f"{format_bold('News', escape=False)}\n\n{safe_caption}"
    
    # Send with HTML
    try:
        await bot.send_photo(
            chat_id=user_id,
            photo=photo,
            caption=full_caption,
            parse_mode="HTML"
        )
    except Exception as e:
        # Fallback: send photo without caption, then text
        await bot.send_photo(chat_id=user_id, photo=photo)
        await send_safe_message(
            bot=bot,
            chat_id=user_id,
            text=full_caption,
            parse_mode="HTML",
            fallback_to_plain=True
        )
```

## Example 7: Translated Content

### ❌ Before (Unsafe)
```python
async def send_translated_news(bot, user_id, news, lang):
    # Translate
    translated = await translate_text(news, lang)
    
    # Send (DANGEROUS - translated text not escaped!)
    await bot.send_message(
        chat_id=user_id,
        text=f"**News**\n\n{translated}",
        parse_mode='Markdown'
    )
```

### ✅ After (Safe)
```python
from utils.telegram_formatter import build_news_message, send_safe_message

async def send_translated_news(bot, user_id, news, lang):
    # Translate
    translated = await translate_text(news, lang)
    
    # Build safe message (auto-escapes translated content)
    message = build_news_message(
        category_name="News",
        news_content=translated,
        footer="📰 More news",
        escape_content=True  # CRITICAL for translated text!
    )
    
    # Send safely
    await send_safe_message(
        bot=bot,
        chat_id=user_id,
        text=message,
        parse_mode="HTML",
        fallback_to_plain=True
    )
```

## Example 8: List/Menu

### ❌ Before (Unsafe)
```python
async def show_menu(update, context, items):
    menu = "**MENU**\n\n"
    for i, item in enumerate(items, 1):
        menu += f"{i}. {item}\n"
    
    await update.message.reply_text(menu, parse_mode='Markdown')
```

### ✅ After (Safe)
```python
from utils.telegram_formatter import format_bold, escape_html, send_safe_message

async def show_menu(update, context, items):
    # Build menu
    lines = [format_bold("MENU", escape=False), ""]
    
    for i, item in enumerate(items, 1):
        safe_item = escape_html(item)
        lines.append(f"{i}. {safe_item}")
    
    message = "\n".join(lines)
    
    # Send safely
    await send_safe_message(
        bot=context.bot,
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode="HTML",
        fallback_to_plain=True
    )
```

## Example 9: Complex Formatting

### ❌ Before (Unsafe)
```python
async def send_report(update, context, data):
    report = f"""
**DAILY REPORT**

*Statistics:*
- Users: {data['users']}
- News: {data['news']}
- Errors: {data['errors']}

*Status:* {data['status']}
"""
    
    await update.message.reply_text(report, parse_mode='Markdown')
```

### ✅ After (Safe)
```python
from utils.telegram_formatter import format_bold, format_italic, escape_html, send_safe_message

async def send_report(update, context, data):
    # Escape all data
    safe_data = {k: escape_html(str(v)) for k, v in data.items()}
    
    # Build report
    report = f"""{format_bold("DAILY REPORT", escape=False)}

{format_italic("Statistics:", escape=False)}
- Users: {safe_data['users']}
- News: {safe_data['news']}
- Errors: {safe_data['errors']}

{format_italic("Status:", escape=False)} {safe_data['status']}
"""
    
    # Send safely
    await send_safe_message(
        bot=context.bot,
        chat_id=update.effective_chat.id,
        text=report,
        parse_mode="HTML",
        fallback_to_plain=True
    )
```

## Example 10: Callback Query Response

### ❌ Before (Unsafe)
```python
async def handle_callback(update, context):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        f"**Selected:** {query.data}",
        parse_mode='Markdown'
    )
```

### ✅ After (Safe)
```python
from utils.telegram_formatter import format_bold, escape_html

async def handle_callback(update, context):
    query = update.callback_query
    await query.answer()
    
    # Escape callback data
    safe_data = escape_html(query.data)
    
    # Build message
    message = f"{format_bold('Selected:', escape=False)} {safe_data}"
    
    # Edit message
    try:
        await query.edit_message_text(
            text=message,
            parse_mode="HTML"
        )
    except Exception as e:
        # Fallback: send new message
        await send_safe_message(
            bot=context.bot,
            chat_id=query.message.chat_id,
            text=message,
            parse_mode="HTML",
            fallback_to_plain=True
        )
```

## 🎯 Key Takeaways

### Always Remember:

1. **Use HTML** instead of Markdown
2. **Escape ALL external content** with `escape_html()`
3. **Use `send_safe_message()`** with `fallback_to_plain=True`
4. **Use message templates** when available
5. **Test with real data** including special characters

### Common Pattern:

```python
from utils.telegram_formatter import escape_html, send_safe_message

# 1. Escape external content
safe_content = escape_html(external_data)

# 2. Build message
message = f"<b>Title</b>\n\n{safe_content}"

# 3. Send safely
await send_safe_message(
    bot=bot,
    chat_id=chat_id,
    text=message,
    parse_mode="HTML",
    fallback_to_plain=True
)
```

---

**Remember:** When in doubt, escape! Better safe than sorry. 🛡️

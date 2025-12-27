"""
🛡️ PRODUCTION-GRADE TELEGRAM MESSAGE FORMATTER
Solves all parse_mode issues for multilingual news bot

CRITICAL FEATURES:
- HTML escaping for ALL external content
- Automatic fallback to plain text on parse errors
- Safe message templates
- Error logging and debugging
- Works with translated and user-generated content
"""

import html
import logging
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class ParseMode(Enum):
    """Supported Telegram parse modes"""
    HTML = "HTML"
    MARKDOWN = "MarkdownV2"
    PLAIN = None


# ============================================================================
# CHOICE: HTML is the SAFEST parse_mode for production
# ============================================================================
# WHY HTML?
# 1. More predictable escaping rules (only 5 characters: < > & " ')
# 2. MarkdownV2 has 18+ special characters that need escaping
# 3. HTML is more forgiving with whitespace
# 4. Better for multilingual content (Cyrillic, Arabic, etc.)
# 5. Easier to debug when things go wrong
# 6. Industry standard for web content
# ============================================================================

SAFE_PARSE_MODE = ParseMode.HTML


def escape_html(text: str) -> str:
    """
    Escape HTML special characters to prevent parse errors
    
    CRITICAL: Use this for ALL external/user-generated content:
    - News text from Telegram channels
    - Translated text
    - User input
    - Database content
    
    Args:
        text: Raw text that may contain HTML special characters
        
    Returns:
        HTML-safe text
        
    Example:
        >>> escape_html("Price: $100 <discount>")
        'Price: $100 &lt;discount&gt;'
    """
    if not text:
        return ""
    
    # Python's html.escape handles: < > & " '
    return html.escape(str(text), quote=True)


def escape_markdown_v2(text: str) -> str:
    """
    Escape MarkdownV2 special characters
    
    WARNING: MarkdownV2 has many special characters!
    Use HTML instead for production.
    
    Special chars: _ * [ ] ( ) ~ ` > # + - = | { } . !
    """
    if not text:
        return ""
    
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text


def format_bold(text: str, escape: bool = True) -> str:
    """
    Format text as bold (HTML)
    
    Args:
        text: Text to make bold
        escape: Whether to escape HTML characters (default: True)
        
    Returns:
        HTML bold text
    """
    if escape:
        text = escape_html(text)
    return f"<b>{text}</b>"


def format_italic(text: str, escape: bool = True) -> str:
    """Format text as italic (HTML)"""
    if escape:
        text = escape_html(text)
    return f"<i>{text}</i>"


def format_code(text: str, escape: bool = True) -> str:
    """Format text as code (HTML)"""
    if escape:
        text = escape_html(text)
    return f"<code>{text}</code>"


def format_link(text: str, url: str, escape_text: bool = True) -> str:
    """
    Format text as hyperlink (HTML)
    
    Args:
        text: Link text to display
        url: URL to link to
        escape_text: Whether to escape the display text
        
    Returns:
        HTML link
    """
    if escape_text:
        text = escape_html(text)
    # URL should NOT be escaped
    return f'<a href="{url}">{text}</a>'


# ============================================================================
# MESSAGE TEMPLATES FOR NEWS BOT
# ============================================================================

def build_news_message(
    category_name: str,
    news_content: str,
    footer: str,
    source_link: Optional[str] = None,
    escape_content: bool = True
) -> str:
    """
    Build a safe news message with proper HTML formatting
    
    PRODUCTION-SAFE: All external content is escaped
    
    Args:
        category_name: Category name (e.g., "🏛 Политика")
        news_content: Main news text (WILL BE ESCAPED)
        footer: Footer text (e.g., "📰 Other categories /interests")
        source_link: Optional source URL
        escape_content: Whether to escape news_content (default: True)
        
    Returns:
        HTML-formatted message ready for Telegram
        
    Example:
        >>> msg = build_news_message(
        ...     category_name="🏛 Politics",
        ...     news_content="Trump said: <We need Greenland>",
        ...     footer="📰 Other categories /interests"
        ... )
        >>> # Output: Safe HTML with escaped < >
    """
    # Escape external content
    if escape_content:
        news_content = escape_html(news_content)
    
    # Category name is usually safe (from our database), but escape to be sure
    category_name = escape_html(category_name)
    footer = escape_html(footer)
    
    # Build message
    parts = [
        format_bold(category_name, escape=False),  # Already escaped
        "",  # Empty line
        news_content,  # Already escaped
        "",  # Empty line
        "━━━━━━━━━━━━━━━━━━━━",
        "",  # Empty line
        footer  # Already escaped
    ]
    
    # Add source link if provided
    if source_link:
        parts.append("")
        parts.append(format_link("📰 Источник", source_link, escape_text=False))
    
    return "\n".join(parts)


def build_status_message(
    header: str,
    fields: Dict[str, str],
    escape_values: bool = True
) -> str:
    """
    Build a safe status/profile message
    
    Args:
        header: Message header (e.g., "👤 PROFILE")
        fields: Dictionary of field_name: field_value
        escape_values: Whether to escape field values
        
    Returns:
        HTML-formatted status message
        
    Example:
        >>> msg = build_status_message(
        ...     header="👤 PROFILE",
        ...     fields={
        ...         "Username": "@john_doe",
        ...         "Language": "English",
        ...         "Plan": "Premium"
        ...     }
        ... )
    """
    header = escape_html(header)
    
    lines = [format_bold(header, escape=False)]
    lines.append("")
    
    for field_name, field_value in fields.items():
        field_name = escape_html(field_name)
        if escape_values:
            field_value = escape_html(field_value)
        lines.append(f"┌ {format_bold(field_name, escape=False)}: {field_value}")
    
    return "\n".join(lines)


def build_error_message(
    error_title: str,
    error_description: str,
    escape: bool = True
) -> str:
    """
    Build a safe error message
    
    Args:
        error_title: Error title (e.g., "❌ ERROR")
        error_description: Error description
        escape: Whether to escape content
        
    Returns:
        HTML-formatted error message
    """
    if escape:
        error_title = escape_html(error_title)
        error_description = escape_html(error_description)
    
    return f"{format_bold(error_title, escape=False)}\n\n{error_description}"


# ============================================================================
# SAFE MESSAGE SENDER WITH AUTOMATIC FALLBACK
# ============================================================================

async def send_safe_message(
    bot,
    chat_id: int,
    text: str,
    parse_mode: Optional[str] = "HTML",
    fallback_to_plain: bool = True,
    **kwargs
) -> Optional[Any]:
    """
    Send message with automatic fallback to plain text on parse errors
    
    PRODUCTION-SAFE: Never fails due to parse_mode issues
    
    Args:
        bot: Telegram bot instance
        chat_id: Chat ID to send to
        text: Message text (should be pre-formatted with HTML)
        parse_mode: Parse mode to use (default: HTML)
        fallback_to_plain: If True, retry as plain text on error
        **kwargs: Additional arguments for send_message
        
    Returns:
        Sent message object or None on failure
        
    Example:
        >>> await send_safe_message(
        ...     bot=bot,
        ...     chat_id=123456,
        ...     text=build_news_message(...),
        ...     parse_mode="HTML"
        ... )
    """
    try:
        # Try sending with parse_mode
        message = await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            **kwargs
        )
        return message
        
    except Exception as e:
        error_msg = str(e).lower()
        
        # Check if it's a parse error
        if any(keyword in error_msg for keyword in [
            'parse', 'entity', 'entities', 'markdown', 'html', 'can\'t parse'
        ]):
            logger.error(
                f"Parse error for chat {chat_id}: {e}\n"
                f"Parse mode: {parse_mode}\n"
                f"Text preview: {text[:200]}..."
            )
            
            if fallback_to_plain:
                try:
                    # Strip HTML tags for plain text
                    plain_text = strip_html_tags(text)
                    
                    logger.warning(f"Falling back to plain text for chat {chat_id}")
                    
                    message = await bot.send_message(
                        chat_id=chat_id,
                        text=plain_text,
                        parse_mode=None,  # No formatting
                        **kwargs
                    )
                    return message
                    
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed for chat {chat_id}: {fallback_error}")
                    return None
        else:
            # Not a parse error, re-raise
            logger.error(f"Non-parse error for chat {chat_id}: {e}")
            raise


def strip_html_tags(text: str) -> str:
    """
    Remove HTML tags from text (for plain text fallback)
    
    Args:
        text: HTML-formatted text
        
    Returns:
        Plain text without HTML tags
    """
    import re
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Unescape HTML entities
    text = html.unescape(text)
    return text


# ============================================================================
# DEBUGGING HELPERS
# ============================================================================

def validate_html(text: str) -> tuple[bool, Optional[str]]:
    """
    Validate HTML formatting before sending
    
    Args:
        text: HTML text to validate
        
    Returns:
        (is_valid, error_message)
        
    Example:
        >>> is_valid, error = validate_html("<b>Test</b>")
        >>> if not is_valid:
        ...     print(f"Invalid HTML: {error}")
    """
    try:
        from html.parser import HTMLParser
        
        class TelegramHTMLValidator(HTMLParser):
            def __init__(self):
                super().__init__()
                self.errors = []
                self.tag_stack = []
                self.allowed_tags = {'b', 'i', 'u', 's', 'code', 'pre', 'a', 'tg-spoiler', 'tg-emoji'}
            
            def handle_starttag(self, tag, attrs):
                if tag not in self.allowed_tags:
                    self.errors.append(f"Unsupported tag: <{tag}>")
                self.tag_stack.append(tag)
            
            def handle_endtag(self, tag):
                if not self.tag_stack:
                    self.errors.append(f"Closing tag without opening: </{tag}>")
                elif self.tag_stack[-1] != tag:
                    self.errors.append(f"Mismatched tags: <{self.tag_stack[-1]}> vs </{tag}>")
                else:
                    self.tag_stack.pop()
        
        validator = TelegramHTMLValidator()
        validator.feed(text)
        
        if validator.errors:
            return False, "; ".join(validator.errors)
        
        if validator.tag_stack:
            return False, f"Unclosed tags: {', '.join(validator.tag_stack)}"
        
        return True, None
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def debug_parse_error(text: str, error: Exception) -> str:
    """
    Generate detailed debug information for parse errors
    
    Args:
        text: Text that caused the error
        error: Exception that was raised
        
    Returns:
        Debug information string
    """
    debug_info = [
        "=" * 60,
        "TELEGRAM PARSE ERROR DEBUG INFO",
        "=" * 60,
        f"Error: {str(error)}",
        f"Text length: {len(text)} characters",
        "",
        "Text preview (first 500 chars):",
        "-" * 60,
        text[:500],
        "-" * 60,
        "",
        "HTML validation:",
    ]
    
    is_valid, validation_error = validate_html(text)
    if is_valid:
        debug_info.append("✅ HTML structure is valid")
    else:
        debug_info.append(f"❌ HTML validation failed: {validation_error}")
    
    debug_info.append("=" * 60)
    
    return "\n".join(debug_info)


# ============================================================================
# BEST PRACTICES SUMMARY
# ============================================================================

"""
🎯 BEST PRACTICES TO AVOID PARSE_MODE BUGS FOREVER:

1. ✅ ALWAYS use HTML (not Markdown/MarkdownV2)
   - Simpler escaping rules
   - More predictable behavior
   - Better for multilingual content

2. ✅ ALWAYS escape external content
   - News from channels: escape_html()
   - Translated text: escape_html()
   - User input: escape_html()
   - Database content: escape_html()

3. ✅ NEVER trust external content
   - Even if it "looks safe"
   - Even if it's from your own channels
   - Even if it worked before

4. ✅ ALWAYS use send_safe_message()
   - Automatic fallback to plain text
   - Error logging for debugging
   - Never fails silently

5. ✅ TEST with real data
   - Test with Cyrillic, Arabic, Chinese
   - Test with special characters: < > & " '
   - Test with very long messages
   - Test with translated content

6. ❌ NEVER do this:
   - f"<b>{user_input}</b>"  # WRONG! Escape first!
   - parse_mode='Markdown'  # WRONG! Use HTML!
   - Ignore parse errors  # WRONG! Log and fallback!
   - Mix escaped and unescaped content  # WRONG! Be consistent!

7. ✅ DEBUGGING checklist:
   - Check error message for "parse" or "entity"
   - Use validate_html() to check structure
   - Use debug_parse_error() for detailed info
   - Check logs for patterns
   - Test with minimal example

8. ✅ PRODUCTION checklist:
   - All external content escaped ✓
   - Using send_safe_message() ✓
   - Fallback to plain text enabled ✓
   - Error logging configured ✓
   - Tested with multilingual content ✓
"""

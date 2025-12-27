"""
🧪 COMPREHENSIVE TEST SUITE FOR TELEGRAM FORMATTER
Tests all edge cases and potential parse_mode issues
"""

import asyncio
from utils.telegram_formatter import (
    escape_html,
    build_news_message,
    build_status_message,
    build_error_message,
    validate_html,
    format_bold,
    format_italic,
    format_link,
    strip_html_tags
)


def test_escape_html():
    """Test HTML escaping for dangerous characters"""
    print("\n" + "="*60)
    print("TEST 1: HTML Escaping")
    print("="*60)
    
    test_cases = [
        # (input, expected_output, description)
        ("Hello World", "Hello World", "Normal text"),
        ("Price: $100 <discount>", "Price: $100 &lt;discount&gt;", "Angle brackets"),
        ('Say "Hello"', 'Say &quot;Hello&quot;', "Quotes"),
        ("A & B", "A &amp; B", "Ampersand"),
        ("<script>alert('xss')</script>", "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;", "XSS attempt"),
        ("Цена: 100₽", "Цена: 100₽", "Cyrillic text"),
        ("السعر: 100", "السعر: 100", "Arabic text"),
        ("价格：100", "价格：100", "Chinese text"),
    ]
    
    passed = 0
    failed = 0
    
    for input_text, expected, description in test_cases:
        result = escape_html(input_text)
        if result == expected:
            print(f"✅ {description}")
            print(f"   Input:    {input_text}")
            print(f"   Output:   {result}")
            passed += 1
        else:
            print(f"❌ {description}")
            print(f"   Input:    {input_text}")
            print(f"   Expected: {expected}")
            print(f"   Got:      {result}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_news_message_building():
    """Test news message building with various content"""
    print("\n" + "="*60)
    print("TEST 2: News Message Building")
    print("="*60)
    
    test_cases = [
        {
            "name": "Simple news",
            "category": "🏛 Politics",
            "content": "President signed new law",
            "footer": "📰 Other categories /interests"
        },
        {
            "name": "News with special characters",
            "category": "💰 Economy",
            "content": "Dollar rate: $1 = 12,500 UZS <up 2%>",
            "footer": "📰 Boshqa kategoriyalar /interests"
        },
        {
            "name": "News with quotes",
            "category": "👥 Society",
            "content": 'Minister said: "Education is priority"',
            "footer": "📰 Другие категории /interests"
        },
        {
            "name": "Multilingual news (Cyrillic)",
            "category": "🏛 Сиёсат",
            "content": "Президент подписал новый закон о <важных изменениях>",
            "footer": "📰 Бошқа категориялар учун /interests"
        },
        {
            "name": "Long news with HTML-like content",
            "category": "💻 Technology",
            "content": "Apple released <iPhone 16> with new features: <AI>, <5G>, and <better camera>. Price starts at $999.",
            "footer": "📰 Other categories /interests"
        }
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        try:
            message = build_news_message(
                category_name=test_case["category"],
                news_content=test_case["content"],
                footer=test_case["footer"],
                escape_content=True
            )
            
            # Validate HTML
            is_valid, error = validate_html(message)
            
            if is_valid:
                print(f"✅ {test_case['name']}")
                print(f"   Category: {test_case['category']}")
                print(f"   Content:  {test_case['content'][:50]}...")
                print(f"   Valid HTML: Yes")
                passed += 1
            else:
                print(f"❌ {test_case['name']}")
                print(f"   Category: {test_case['category']}")
                print(f"   Content:  {test_case['content'][:50]}...")
                print(f"   Valid HTML: No")
                print(f"   Error: {error}")
                failed += 1
                
        except Exception as e:
            print(f"❌ {test_case['name']}")
            print(f"   Exception: {str(e)}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_html_validation():
    """Test HTML validation"""
    print("\n" + "="*60)
    print("TEST 3: HTML Validation")
    print("="*60)
    
    test_cases = [
        ("<b>Bold text</b>", True, "Valid bold"),
        ("<i>Italic text</i>", True, "Valid italic"),
        ("<b>Bold <i>and italic</i></b>", True, "Nested tags"),
        ("<b>Unclosed bold", False, "Unclosed tag"),
        ("<b>Wrong</i>", False, "Mismatched tags"),
        ("<script>alert('xss')</script>", False, "Unsupported tag"),
        ("<a href='https://example.com'>Link</a>", True, "Valid link"),
        ("<b>Test</b> <i>Test</i>", True, "Multiple tags"),
    ]
    
    passed = 0
    failed = 0
    
    for html_text, expected_valid, description in test_cases:
        is_valid, error = validate_html(html_text)
        
        if is_valid == expected_valid:
            print(f"✅ {description}")
            print(f"   HTML: {html_text}")
            print(f"   Valid: {is_valid}")
            if error:
                print(f"   Error: {error}")
            passed += 1
        else:
            print(f"❌ {description}")
            print(f"   HTML: {html_text}")
            print(f"   Expected valid: {expected_valid}")
            print(f"   Got valid: {is_valid}")
            if error:
                print(f"   Error: {error}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_formatting_functions():
    """Test formatting helper functions"""
    print("\n" + "="*60)
    print("TEST 4: Formatting Functions")
    print("="*60)
    
    test_cases = [
        ("format_bold", format_bold, "Test", "<b>Test</b>"),
        ("format_bold with escape", format_bold, "Test <tag>", "<b>Test &lt;tag&gt;</b>"),
        ("format_italic", format_italic, "Test", "<i>Test</i>"),
        ("format_link", lambda t: format_link(t, "https://example.com"), "Click here", '<a href="https://example.com">Click here</a>'),
        ("format_link with escape", lambda t: format_link(t, "https://example.com"), "Click <here>", '<a href="https://example.com">Click &lt;here&gt;</a>'),
    ]
    
    passed = 0
    failed = 0
    
    for name, func, input_text, expected in test_cases:
        try:
            result = func(input_text)
            if result == expected:
                print(f"✅ {name}")
                print(f"   Input:  {input_text}")
                print(f"   Output: {result}")
                passed += 1
            else:
                print(f"❌ {name}")
                print(f"   Input:    {input_text}")
                print(f"   Expected: {expected}")
                print(f"   Got:      {result}")
                failed += 1
        except Exception as e:
            print(f"❌ {name}")
            print(f"   Exception: {str(e)}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_strip_html_tags():
    """Test HTML tag stripping for plain text fallback"""
    print("\n" + "="*60)
    print("TEST 5: HTML Tag Stripping")
    print("="*60)
    
    test_cases = [
        ("<b>Bold</b>", "Bold", "Simple bold"),
        ("<b>Bold</b> and <i>italic</i>", "Bold and italic", "Multiple tags"),
        ("<a href='url'>Link</a>", "Link", "Link tag"),
        ("Plain text", "Plain text", "No tags"),
        ("<b>Test &lt;tag&gt;</b>", "Test <tag>", "Escaped entities"),
    ]
    
    passed = 0
    failed = 0
    
    for html_text, expected, description in test_cases:
        result = strip_html_tags(html_text)
        if result == expected:
            print(f"✅ {description}")
            print(f"   HTML:  {html_text}")
            print(f"   Plain: {result}")
            passed += 1
        else:
            print(f"❌ {description}")
            print(f"   HTML:     {html_text}")
            print(f"   Expected: {expected}")
            print(f"   Got:      {result}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_real_world_scenarios():
    """Test real-world scenarios from production"""
    print("\n" + "="*60)
    print("TEST 6: Real-World Scenarios")
    print("="*60)
    
    # Scenario 1: News from Telegram channel with HTML-like content
    news_from_channel = """
    «Biz Grenlandiyani olishimiz kerak» - Tramp mineral resurslarga boy orolga ko'z tikmoqda
    
    «Agar Grenlandiyaga qarasangiz, butun qirg'oq bo'ylab rus va Xitoy kemalarini ko'rasiz. 
    U bizga milliy xavfsizlik uchun zarur, uni olishimiz kerak», - dedi AQSh prezidenti.
    
    Tramp shuningdek, Grenlandiya bo'yicha maxsus elchi tayinlab, u jarayonga «bosh-qosh bo'lishini» aytdi.
    """
    
    # Scenario 2: Translated news with special characters
    translated_news_ru = """
    «Нам нужна Гренландия» - Трамп нацелился на остров, богатый минеральными ресурсами
    
    «Если посмотреть на Гренландию, вы увидите российские и китайские корабли вдоль всего побережья. 
    Она нам нужна для национальной безопасности, мы должны её получить», - заявил президент США.
    
    Трамп также назначил специального посланника по Гренландии, заявив, что он будет «руководить процессом».
    """
    
    # Scenario 3: News with price and special symbols
    economy_news = """
    Dollar kursi: $1 = 12,500 so'm <+2.5%>
    
    Markaziy bank ma'lumotlariga ko'ra, dollar kursi 2.5% oshdi.
    Ekspertlar: "Bu o'sish vaqtinchalik" deyishmoqda.
    
    Boshqa valyutalar:
    - Euro: €1 = 13,200 so'm
    - Rubl: ₽100 = 12,800 so'm
    """
    
    scenarios = [
        ("News from channel", "🌍 Dunyo", news_from_channel),
        ("Translated news (Russian)", "🌍 Мир", translated_news_ru),
        ("Economy news with symbols", "💰 Iqtisod", economy_news),
    ]
    
    passed = 0
    failed = 0
    
    for name, category, content in scenarios:
        try:
            message = build_news_message(
                category_name=category,
                news_content=content.strip(),
                footer="📰 Other categories /interests",
                escape_content=True
            )
            
            is_valid, error = validate_html(message)
            
            if is_valid:
                print(f"✅ {name}")
                print(f"   Category: {category}")
                print(f"   Length: {len(message)} chars")
                print(f"   Valid HTML: Yes")
                passed += 1
            else:
                print(f"❌ {name}")
                print(f"   Category: {category}")
                print(f"   Valid HTML: No")
                print(f"   Error: {error}")
                failed += 1
                
        except Exception as e:
            print(f"❌ {name}")
            print(f"   Exception: {str(e)}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def run_all_tests():
    """Run all tests"""
    print("\n" + "🧪"*30)
    print("TELEGRAM FORMATTER TEST SUITE")
    print("🧪"*30)
    
    results = []
    
    results.append(("HTML Escaping", test_escape_html()))
    results.append(("News Message Building", test_news_message_building()))
    results.append(("HTML Validation", test_html_validation()))
    results.append(("Formatting Functions", test_formatting_functions()))
    results.append(("HTML Tag Stripping", test_strip_html_tags()))
    results.append(("Real-World Scenarios", test_real_world_scenarios()))
    
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    
    total_passed = sum(1 for _, passed in results if passed)
    total_failed = len(results) - total_passed
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*60)
    print(f"Total: {total_passed}/{len(results)} tests passed")
    print("="*60)
    
    if total_failed == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("Your Telegram formatter is production-ready!")
    else:
        print(f"\n⚠️  {total_failed} test(s) failed. Please review and fix.")
    
    return total_failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)

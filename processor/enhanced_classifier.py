"""
Yaxshilangan classifier - AI va keyword-based kombinatsiya
"""
from processor.classifier import classify_news as keyword_classify
from processor.ai_analyzer import analyze_with_ai, SYSTEM_PROMPT
from typing import Dict, Optional


def classify_news_enhanced(text: str, channel: str) -> Dict:
    """
    Yangilikni tahlil qilish (AI + keyword-based)
    
    Args:
        text: Post matni
        channel: Kanal username
    
    Returns:
        {
            "category": str,
            "is_news": bool,
            "summary": str (agar AI ishlatilsa),
            "importance": str (agar AI ishlatilsa),
            "method": "ai" | "keyword"
        }
    """
    # Avval AI bilan sinab ko'rish
    ai_result = analyze_with_ai(text, channel)
    
    if ai_result and ai_result.get('is_news'):
        return {
            "category": ai_result['category'],
            "is_news": True,
            "summary": ai_result.get('summary', text[:200]),
            "importance": ai_result.get('importance', 'medium'),
            "method": "ai"
        }
    
    # AI ishlamasa yoki yangilik emas desa - keyword-based
    category = keyword_classify(text)
    
    # Agar kategoriya topilmasa - yangilik emas
    is_news = category != 'umumiy'
    
    return {
        "category": category,
        "is_news": is_news,
        "summary": text[:200] + "..." if len(text) > 200 else text,
        "importance": "medium",
        "method": "keyword"
    }


def get_ai_prompt() -> str:
    """AI analyzer uchun system prompt ni qaytarish"""
    return SYSTEM_PROMPT

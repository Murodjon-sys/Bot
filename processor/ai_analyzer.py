"""
AI-based news analyzer
OpenAI yoki boshqa LLM bilan ishlash uchun
"""
import json
from typing import Optional, Dict

# AI Analyzer uchun system prompt
SYSTEM_PROMPT = """
You are an AI engine for a premium Telegram News Bot for Uzbekistan.

Your trusted news sources are ONLY:
- @uzreport
- @daryo
- @gazetauz
- @kunuz

Do NOT process content from any other sources.

────────────────────────────
YOUR TASK FOR EACH INCOMING POST:

1. Verify content:
   - Must be factual NEWS
   - No ads, no opinions, no entertainment

2. Assign ONE category:
   Politics | Economy | Society | Technology | World | Health

3. Breaking news detection:
   Mark as BREAKING if it involves:
   - Government decisions
   - Laws or regulations
   - Emergencies
   - National-level events

4. Importance scoring:
   - High: laws, emergencies, government actions
   - Medium: economy, social issues, official statements
   - Low: routine or minor updates

5. Duplicate control:
   - If similar news already sent within last 12 hours, ignore

6. Summary generation:
   - Uzbek language (Latin)
   - Max 2 sentences
   - Neutral tone
   - No emojis
   - No clickbait

7. Change detection (if applicable):
   - If news modifies a rule or law, output "before" and "after" comparison

8. Output strictly in JSON format:
{
    "send": true | false,
    "source": "channel_username",
    "category": "Politics | Economy | Society | Technology | World | Health",
    "importance": "high | medium | low",
    "breaking": true | false,
    "summary": "short neutral summary",
    "before": "optional - old rule/law",
    "after": "optional - new rule/law",
    "original_link": "post_link",
    "timestamp": "ISO-8601"
}

IMPORTANT RULES:
- Accuracy is more important than speed
- Never invent facts
- Never add personal opinions
- If unsure, set "send": false
"""


def analyze_with_ai(text: str, channel: str) -> Optional[Dict]:
    """
    AI bilan yangilikni tahlil qilish
    
    Args:
        text: Post matni
        channel: Kanal username
    
    Returns:
        {
            "category": str,
            "is_breaking": bool,
            "importance": str
        }
    """
    from config import OPENAI_API_KEY
    
    # Agar OpenAI API key yo'q bo'lsa - None qaytarish
    if not OPENAI_API_KEY or OPENAI_API_KEY == '':
        return None
    
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        
        # Kategoriyalarni aniqlash uchun prompt
        prompt = f"""
Quyidagi yangilikni tahlil qiling va kategoriyasini aniqlang.

KATEGORIYALAR:
- siyosat: prezident, hukumat, qonun, vazir, parlament, davlat
- iqtisod: dollar, narx, bank, biznes, investitsiya, soliq, valyuta
- jamiyat: ta'lim, madaniyat, maktab, universitet, festival, konsert
- sport: futbol, basketbol, o'yin, chempion, liga, medal
- texnologiya: AI, dastur, telefon, kompyuter, internet, Apple, Google
- dunyo: xalqaro, urush, tinchlik, AQSh, Rossiya, Xitoy
- salomatlik: kasallik, shifokor, shifoxona, dori, vitamin
- obhavo: ob-havo, harorat, yomg'ir, qor, shamol, prognoz
- other: boshqa

YANGILIK:
{text[:500]}

Faqat kategoriya nomini qaytaring (bitta so'z): siyosat, iqtisod, jamiyat, sport, texnologiya, dunyo, salomatlik, obhavo, yoki other
"""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Siz yangiliklar kategoriyasini aniqlaydigan AI assistentsiz. Faqat kategoriya nomini qaytaring."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=20
        )
        
        category = response.choices[0].message.content.strip().lower()
        
        # Kategoriya validatsiya
        valid_categories = ['siyosat', 'iqtisod', 'jamiyat', 'sport', 'texnologiya', 'dunyo', 'salomatlik', 'obhavo', 'other']
        if category not in valid_categories:
            return None
        
        return {
            "category": category,
            "is_breaking": False,  # TODO: breaking detection
            "importance": "medium"
        }
        
    except Exception as e:
        print(f"⚠️ AI analyzer xato: {e}")
        return None


def is_duplicate(new_summary: str, existing_summaries: list) -> bool:
    """
    Yangilik dublikat ekanligini tekshirish
    
    Args:
        new_summary: Yangi yangilik summary
        existing_summaries: Mavjud summarylar ro'yxati
    
    Returns:
        True agar dublikat bo'lsa
    """
    # Oddiy similarity check
    # TODO: Yanada murakkab similarity algorithm (cosine similarity, etc.)
    
    new_words = set(new_summary.lower().split())
    
    for existing in existing_summaries:
        existing_words = set(existing.lower().split())
        
        # Agar 70% so'zlar bir xil bo'lsa - dublikat
        common = new_words & existing_words
        similarity = len(common) / max(len(new_words), len(existing_words))
        
        if similarity > 0.7:
            return True
    
    return False

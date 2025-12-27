"""
Yangilik matnlarini tarjima qilish xizmati
Google Translate API (bepul) dan foydalanadi
"""
import asyncio
import urllib.parse
import urllib.request
import json
from functools import lru_cache

# Til kodlarini mapping (bizning kodlar -> Google Translate kodlari)
LANG_MAP = {
    'uz': 'uz',           # O'zbek (lotin)
    'uz_cyrl': 'uz',      # O'zbek (kirill) - Google Translate uz kodini ishlatadi
    'ru': 'ru',           # Rus
    'en': 'en'            # Ingliz
}

@lru_cache(maxsize=1000)
def _translate_sync(text: str, dest_lang: str) -> str:
    """
    Tarjimani sinxron amalga oshirish (kesh bilan)
    Google Translate API (bepul) dan foydalanadi
    
    Args:
        text: Tarjima qilinadigan matn
        dest_lang: Maqsad til kodi
    
    Returns:
        Tarjima qilingan matn
    """
    try:
        # Google Translate til kodini olish
        google_lang = LANG_MAP.get(dest_lang, 'uz')
        
        # URL yaratish
        encoded_text = urllib.parse.quote(text)
        url = f"http://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={google_lang}&dt=t&q={encoded_text}"
        
        # So'rov yuborish
        with urllib.request.urlopen(url, timeout=10) as response:
            data = response.read()
            result = json.loads(data)
            
            # Tarjimani olish
            if result and len(result) > 0 and result[0]:
                translated = ""
                for item in result[0]:
                    if item and len(item) > 0:
                        translated += item[0]
                return translated.strip()
        
        return text
    except Exception as e:
        print(f"⚠️ Tarjima xatosi: {e}")
        return text  # Xato bo'lsa asl matnni qaytarish

async def translate_text(text: str, dest_lang: str, source_lang: str = 'auto') -> str:
    """
    Matnni asinxron tarjima qilish
    Google Translate API (bepul) dan foydalanadi
    
    Args:
        text: Tarjima qilinadigan matn
        dest_lang: Maqsad til kodi (uz, uz_cyrl, ru, en)
        source_lang: Manba til kodi (auto - avtomatik aniqlash)
    
    Returns:
        Tarjima qilingan matn
    """
    # Bo'sh matn yoki juda qisqa matn
    if not text or len(text.strip()) < 3:
        return text
    
    # Agar til bir xil bo'lsa, tarjima qilmaslik
    if dest_lang == source_lang:
        return text
    
    try:
        # Sinxron funksiyani asinxron bajarish
        loop = asyncio.get_event_loop()
        translated = await loop.run_in_executor(
            None,
            _translate_sync,
            text,
            dest_lang
        )
        
        # Agar uz_cyrl bo'lsa va matn lotin da bo'lsa, kirill ga o'girish
        if dest_lang == 'uz_cyrl':
            from utils.cyrillic_converter import latin_to_cyrillic, is_cyrillic
            if not is_cyrillic(translated):
                translated = latin_to_cyrillic(translated)
        
        return translated
    except Exception as e:
        print(f"⚠️ Asinxron tarjima xatosi: {e}")
        import traceback
        traceback.print_exc()
        return text

async def detect_language(text: str) -> str:
    """
    Matn tilini aniqlash
    
    Args:
        text: Tahlil qilinadigan matn
    
    Returns:
        Til kodi (uz, ru, en, va h.k.)
    """
    try:
        # Google Translate API orqali til aniqlash
        encoded_text = urllib.parse.quote(text[:100])  # Faqat birinchi 100 belgi
        url = f"http://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={encoded_text}"
        
        loop = asyncio.get_event_loop()
        
        def _detect():
            with urllib.request.urlopen(url, timeout=5) as response:
                data = response.read()
                result = json.loads(data)
                # Til kodini olish (2-indeks)
                if result and len(result) > 2:
                    return result[2]
                return 'uz'
        
        return await loop.run_in_executor(None, _detect)
    except Exception as e:
        print(f"⚠️ Til aniqlash xatosi: {e}")
        return 'uz'  # Default

def clear_translation_cache():
    """Tarjima keshini tozalash"""
    _translate_sync.cache_clear()



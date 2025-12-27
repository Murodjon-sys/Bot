"""
Til aniqlash moduli
"""
import re

def detect_language(text: str) -> str:
    """
    Matnning tilini aniqlash
    
    Returns:
        'uzbek' - O'zbek tili (lotin yoki kirill)
        'russian' - Rus tili
        'english' - Ingliz tili
        'unknown' - Noma'lum
    """
    if not text or len(text.strip()) < 10:
        return 'unknown'
    
    # Kirill harflar soni
    cyrillic_count = len(re.findall(r'[а-яА-ЯёЁ]', text))
    
    # Lotin harflar soni
    latin_count = len(re.findall(r'[a-zA-Z]', text))
    
    # O'zbek kirill harflari
    uzbek_cyrillic = len(re.findall(r'[ўҚқҒғҲҳ]', text))
    
    # Rus tilida ko'p uchraydigan so'zlar
    russian_words = [
        'который', 'которая', 'которые', 'является', 'были', 'было',
        'этого', 'этом', 'этой', 'также', 'более', 'может',
        'после', 'году', 'года', 'лет', 'человек', 'людей',
        'власти', 'властей', 'стран', 'страны', 'российск',
        'сообщ', 'заявил', 'отметил', 'подчеркнул'
    ]
    
    # O'zbek tilida ko'p uchraydigan so'zlar
    uzbek_words = [
        'ва', 'билан', 'учун', 'бўлиб', 'қилди', 'қилиш',
        'бўйича', 'ҳақида', 'ҳам', 'эса', 'лекин', 'аммо',
        'шунингдек', 'ўзбекистон', 'ташкент', 'вилоят'
    ]
    
    text_lower = text.lower()
    
    # Rus so'zlari soni
    russian_word_count = sum(1 for word in russian_words if word in text_lower)
    
    # O'zbek so'zlari soni
    uzbek_word_count = sum(1 for word in uzbek_words if word in text_lower)
    
    # Agar o'zbek kirill harflari bo'lsa - o'zbek
    if uzbek_cyrillic > 0:
        return 'uzbek'
    
    # Agar o'zbek so'zlari ko'p bo'lsa - o'zbek
    if uzbek_word_count >= 2:
        return 'uzbek'
    
    # Agar rus so'zlari ko'p bo'lsa va kirill harflar ko'p - rus
    if russian_word_count >= 2 and cyrillic_count > latin_count:
        return 'russian'
    
    # Agar kirill harflar ko'p lekin rus so'zlari kam - o'zbek (kirill)
    if cyrillic_count > latin_count * 2:
        return 'uzbek'
    
    # Agar lotin harflar ko'p - ingliz yoki o'zbek (lotin)
    if latin_count > cyrillic_count:
        # Ingliz tilida ko'p uchraydigan so'zlar
        english_words = ['the', 'and', 'for', 'with', 'that', 'this', 'from', 'have', 'been']
        english_count = sum(1 for word in english_words if word in text_lower)
        
        if english_count >= 2:
            return 'english'
        else:
            return 'uzbek'  # O'zbek lotin
    
    return 'unknown'


def is_uzbek(text: str) -> bool:
    """
    Matn o'zbek tilida ekanligini tekshirish
    """
    lang = detect_language(text)
    return lang == 'uzbek'

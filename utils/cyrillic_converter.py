"""
O'zbek lotin alifbosini kirill alifbosiga o'girish
"""

# Lotin → Kirill mapping
LATIN_TO_CYRILLIC = {
    'a': 'а', 'b': 'б', 'd': 'д', 'e': 'е', 'f': 'ф', 'g': 'г', 'h': 'ҳ',
    'i': 'и', 'j': 'ж', 'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н', 'o': 'о',
    'p': 'п', 'q': 'қ', 'r': 'р', 's': 'с', 't': 'т', 'u': 'у', 'v': 'в',
    'x': 'х', 'y': 'й', 'z': 'з',
    'A': 'А', 'B': 'Б', 'D': 'Д', 'E': 'Е', 'F': 'Ф', 'G': 'Г', 'H': 'Ҳ',
    'I': 'И', 'J': 'Ж', 'K': 'К', 'L': 'Л', 'M': 'М', 'N': 'Н', 'O': 'О',
    'P': 'П', 'Q': 'Қ', 'R': 'Р', 'S': 'С', 'T': 'Т', 'U': 'У', 'V': 'В',
    'X': 'Х', 'Y': 'Й', 'Z': 'З',
    # Maxsus harflar
    'oʻ': 'ў', 'gʻ': 'ғ', 'sh': 'ш', 'ch': 'ч', 'ng': 'нг', 'yo': 'ё', 'yu': 'ю', 'ya': 'я',
    'Oʻ': 'Ў', 'Gʻ': 'Ғ', 'Sh': 'Ш', 'Ch': 'Ч', 'Ng': 'Нг', 'Yo': 'Ё', 'Yu': 'Ю', 'Ya': 'Я',
    "o'": 'ў', "g'": 'ғ',  # Apostrof variantlari
    "O'": 'Ў', "G'": 'Ғ',
}

def latin_to_cyrillic(text: str) -> str:
    """
    O'zbek lotin matnini kirill ga o'girish
    
    Args:
        text: Lotin alifbosidagi matn
    
    Returns:
        Kirill alifbosidagi matn
    """
    if not text:
        return text
    
    result = text
    
    # Avval ikki harfli kombinatsiyalarni almashtirish
    for latin, cyrillic in sorted(LATIN_TO_CYRILLIC.items(), key=lambda x: len(x[0]), reverse=True):
        if len(latin) > 1:
            result = result.replace(latin, cyrillic)
    
    # Keyin bir harfli almashtirishlar
    for latin, cyrillic in LATIN_TO_CYRILLIC.items():
        if len(latin) == 1:
            result = result.replace(latin, cyrillic)
    
    return result

def is_cyrillic(text: str) -> bool:
    """
    Matn kirill alifbosida yozilganligini tekshirish
    
    Args:
        text: Tekshiriladigan matn
    
    Returns:
        True agar matn asosan kirill da bo'lsa
    """
    if not text:
        return False
    
    # Faqat harflarni sanash
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    
    # Kirill harflar soni
    cyrillic_count = sum(1 for c in letters if '\u0400' <= c <= '\u04FF')
    
    # Agar 50% dan ko'p kirill bo'lsa
    return cyrillic_count / len(letters) > 0.5

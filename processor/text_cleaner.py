import re

def clean_text(text: str) -> str:
    """
    Postni tozalash:
    - Linklar (kun.uz va boshqalar)
    - Hashtag
    - Kanal nomlari
    - Video-related matnlar
    - Reklama matnlari
    - Emoji spam
    - Ortiqcha formatlar (**, ||, ~~)
    """
    if not text:
        return ""
    
    # Markdown linklar ni olib tashlash: [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Linklar ni olib tashlash
    # 1. Kun.uz linki
    text = re.sub(r'https?://kun\.uz/\d+', '', text)
    
    # 2. Boshqa linklar
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)
    
    # Hashtag ni olib tashlash
    text = re.sub(r'#\w+', '', text)
    
    # Kanal nomlarini olib tashlash (oxirida va o'rtada)
    text = re.sub(r'⚡️.*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'👉.*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'📢\s*@\w+.*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'🔗\s*Manba.*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'Manba:?\s*@\w+\s*\n?', '', text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r'Manba:\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)  # Oxirida "Manba:"
    text = re.sub(r'@\w+\s*rasmiy\s*kanali.*\n', '', text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r'rasmiy\s*kanali.*\n', '', text, flags=re.MULTILINE | re.IGNORECASE)
    
    # "rasmiy kanali" har qanday joyda (oxirida ham)
    text = re.sub(r'\s+rasmiy\s+kanali\s*', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'rasmiy\s+kanali', '', text, flags=re.IGNORECASE)
    
    # Kanal nomlari (Kun.uz, Daryo, Gazeta.uz) - har qanday joyda
    text = re.sub(r'Kun\.uz\s*surishtiruvi', 'surishtiruv', text, flags=re.IGNORECASE)
    text = re.sub(r'Kun\.uz\s*jurnalistining', 'jurnalistning', text, flags=re.IGNORECASE)
    text = re.sub(r'Kun\.uz\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Daryo\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Gazeta\.uz\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Yangiliklargruhi\s*', '', text, flags=re.IGNORECASE)
    
    # @kanal nomlari (oxirida va o'rtada)
    text = re.sub(r'\s+@kunuz\s*$', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+@gazetauz\s*$', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+@daryo\s*$', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\|\s*@\w+\s*', '', text, flags=re.IGNORECASE)  # | @kanal
    text = re.sub(r'@\w+\s*\|', '', text, flags=re.IGNORECASE)  # @kanal |
    text = re.sub(r'\s+@\w+\s*$', '', text, flags=re.MULTILINE)  # Har qanday @kanal oxirida
    
    # Telegram so'zi (har qanday joyda)
    text = re.sub(r'\s+Telegram\s*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s+Telegram\s+', ' ', text, flags=re.IGNORECASE)
    
    # Emoji patterns (oxirida va boshida)
    text = re.sub(r'[⚡️👉📢🔗❗️]+\s*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[⚡️👉📢🔗❗️]+\s*', '', text, flags=re.MULTILINE)
    
    # Batafsil — linklar (har qanday joyda)
    text = re.sub(r'Batafsil\s*—.*\n', '', text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r'Подробнее\s*—.*\n', '', text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r'Batafsil\s*—', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Подробнее\s*—', '', text, flags=re.IGNORECASE)
    
    # Video-related matnlar (agar video bo'lmasa olib tashlash)
    text = re.sub(r'📹\s*VIDЕOSHARHNI\s*TOMOSHA\s*QILING.*\n', '', text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r'📹\s*VIDEONI\s*TOMOSHA\s*QILING.*\n', '', text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r'📹\s*VIDEO\s*SHARH.*\n', '', text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r'VIDЕOSHARHNI\s*TOMOSHA\s*QILING', '', text, flags=re.IGNORECASE)
    text = re.sub(r'VIDEONI\s*TOMOSHA\s*QILING', '', text, flags=re.IGNORECASE)
    text = re.sub(r'VIDEO\s*SHARH', '', text, flags=re.IGNORECASE)
    text = re.sub(r'📹\s*', '', text)  # Video emoji
    
    # YANGI: Reklama va kanal nomlari (KUCHAYTIRILGAN)
    # "⚡️ Дунё🌐Уз - Тв да кўрсатмайдиган хабарлар канали!" kabi matnlar
    
    # 1. ⚡️ bilan boshlanadigan butun qatorni olib tashlash
    text = re.sub(r'⚡️[^\n]*\n?', '', text, flags=re.MULTILINE)
    
    # 2. Kategoriya nomlari (emoji bilan) - KIRILL va LOTIN
    # Boshida turgan kategoriya nomlarini olib tashlash
    text = re.sub(r'^🌍\s*Дунё[^\n]*\n?', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'^🌍\s*Dunyo[^\n]*\n?', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'^👥\s*Жамият[^\n]*\n?', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'^👥\s*Jamiyat[^\n]*\n?', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'^⚽\s*Спорт[^\n]*\n?', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'^⚽\s*Sport[^\n]*\n?', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'^💰\s*Иқтисод[^\n]*\n?', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'^💰\s*Iqtisod[^\n]*\n?', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'^🏛\s*Сиёсат[^\n]*\n?', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'^🏛\s*Siyosat[^\n]*\n?', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'^💻\s*Технология[^\n]*\n?', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'^💻\s*Texnologiya[^\n]*\n?', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'^🏥\s*Саломатлик[^\n]*\n?', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'^🏥\s*Salomatlik[^\n]*\n?', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'^🌤\s*Об-ҳаво[^\n]*\n?', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'^🌤\s*Ob-havo[^\n]*\n?', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'^🌤\s*OBHAVO[^\n]*\n?', '', text, flags=re.IGNORECASE | re.MULTILINE)
    
    # 3. Kanal reklama matnlari - KIRILL va LOTIN
    # "Тв да кўрсатмайдиган хабарлар канали" va boshqalar
    text = re.sub(r'[^\n]*?Тв\s*да\s*кўрсатмайдиган[^\n]*?канали[^\n]*?\n?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[^\n]*?Tv\s*da\s*ko\'?rsatmaydigan[^\n]*?kanali[^\n]*?\n?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[^\n]*?хабарлар\s*канали[^\n]*?\n?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[^\n]*?xabarlar\s*kanali[^\n]*?\n?', '', text, flags=re.IGNORECASE)
    
    # 4. Kanal nomlari (Дунё🌐Уз, Kun.uz va boshqalar)
    text = re.sub(r'Дунё\s*🌐\s*Уз[^\n]*?\n?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Дунё[^\n]*?Уз[^\n]*?\n?', '', text, flags=re.IGNORECASE)
    
    # 5. Yolg'iz qolgan belgilar (!, ?, .)
    text = re.sub(r'^\s*[!?.]+\s*$', '', text, flags=re.MULTILINE)
    
    # 6. Eski patternlar (saqlab qolamiz)
    text = re.sub(r'⚡️\s*\*\*.*?\*\*.*?канали.*?\*\*!?', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'⚡️\s*\*\*.*?\*\*.*?канал.*?\*\*!?', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # 7. Umumiy reklama patternlar
    text = re.sub(r'\*\*.*?канали\*\*!?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'канали\s*\*\*!?', '', text, flags=re.IGNORECASE)
    
    # YANGI: Emoji spam va ortiqcha formatlarni tozalash
    # Ko'p emoji ketma-ket (3 tadan ko'p)
    text = re.sub(r'([\U0001F300-\U0001F9FF])\1{2,}', r'\1', text)  # Bir xil emoji 3+ marta
    
    # Yulduzcha (**) formatni olib tashlash
    text = re.sub(r'\*\*\*\*', '', text)  # 4 ta yulduzcha
    text = re.sub(r'\*\*', '', text)  # 2 ta yulduzcha (bold)
    
    # Spoiler (||) formatni olib tashlash
    text = re.sub(r'\|\|', '', text)
    
    # Strikethrough (~~) formatni olib tashlash
    text = re.sub(r'~~', '', text)
    
    # Ortiqcha emoji (raqam emoji spam: 5️⃣5️⃣)
    text = re.sub(r'([0-9]️⃣)\1+', r'\1', text)  # Bir xil raqam emoji 2+ marta
    
    # Ortiqcha bo'sh joy va belgilar
    text = re.sub(r'\s*\*\s*', ' ', text)  # * belgilar atrofidagi bo'sh joylar
    text = re.sub(r'\s*\|\s*', ' ', text)  # | belgilar atrofidagi bo'sh joylar
    
    # Ko'p bo'sh joylarni bitta qilish
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)  # Ko'p qatorlarni ikki qatorga qisqartirish
    
    # Boshida va oxirida bo'sh joylar
    text = text.strip()
    
    # Har bir qatorning boshida va oxirida bo'sh joylar
    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    text = '\n'.join(lines)
    
    # OXIRGI: @kanal nomlarini olib tashlash (eng oxirida)
    text = re.sub(r'\s+@\w+\s*$', '', text, flags=re.MULTILINE)
    
    return text

def extract_preview(text: str, max_length: int = 150) -> str:
    """Qisqa preview yaratish"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

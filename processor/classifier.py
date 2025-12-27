from config import CATEGORIES

def classify_news(text: str, channel: str = None) -> str:
    """
    Yangilikni kategoriyaga ajratish (YAXSHILANGAN)
    1. Avval AI analyzer (agar mavjud bo'lsa)
    2. Keyin keyword-based (kontekst bilan)
    3. Prioritet va kontekst tahlili
    Agar kategoriya topilmasa - None qaytaradi
    """
    if not text or len(text.strip()) < 10:
        return None  # Juda qisqa matn
    
    # AI analyzer ni sinab ko'rish
    try:
        from processor.ai_analyzer import analyze_with_ai
        ai_result = analyze_with_ai(text, channel or 'unknown')
        if ai_result and ai_result.get('category'):
            print(f"   🤖 AI kategoriya: {ai_result['category']}")
            return ai_result['category']
    except Exception as e:
        print(f"   ⚠️ AI analyzer ishlamadi: {e}")
    
    # Keyword-based fallback (YAXSHILANGAN)
    text_lower = text.lower()
    
    # YANGI: Aniq kontekst tekshirish
    # Iqtisod/jamiyat indikatorlari
    economy_indicators = [
        'ish haqi', 'ish haq', 'maosh', 'daromad', 'pul', 'dollar', 'so\'m', 'narx',
        'o\'sish', 'kamayish', 'foiz', 'statistika', 'real', 'nominal',
        'зарплата', 'доход', 'деньги', 'рост', 'снижение', 'процент'
    ]
    
    # Ob-havo aniq indikatorlari
    weather_indicators = [
        'ob-havo', 'obhavo', 'harorat', 'gradus', 'yomg\'ir', 'qor', 'shamol',
        'prognoz', 'iqlim', 'sovuq', 'issiq', 'bulut', 'quyosh',
        'погода', 'температура', 'дождь', 'снег', 'ветер', 'прогноз',
        'weather', 'temperature', 'rain', 'snow', 'forecast'
    ]
    
    # Agar iqtisod indikatorlari ko'p bo'lsa - iqtisod/jamiyat
    economy_count = sum(1 for indicator in economy_indicators if indicator in text_lower)
    weather_count = sum(1 for indicator in weather_indicators if indicator in text_lower)
    
    if economy_count >= 2 and weather_count == 0:
        print(f"   💰 Iqtisod indikatorlari topildi: {economy_count}")
        return 'iqtisod'
    
    if weather_count >= 2 and economy_count == 0:
        print(f"   🌤 Ob-havo indikatorlari topildi: {weather_count}")
        return 'obhavo'
    
    # Har bir kategoriya uchun ball hisoblash (YAXSHILANGAN)
    scores = {}
    for category, keywords in CATEGORIES.items():
        score = 0
        matched_keywords = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # YANGI: Qisqa so'zlarni (2-3 harf) faqat to'liq so'z sifatida tekshirish
            if len(keyword_lower) <= 3:
                # To'liq so'z sifatida tekshirish (word boundary)
                import re
                pattern = r'\b' + re.escape(keyword_lower) + r'\b'
                if re.search(pattern, text_lower):
                    # MAXSUS: "havo" so'zini faqat ob-havo kontekstida hisoblash
                    if keyword_lower in ['havo', 'ҳаво', 'nam', 'нам', 'qor', 'қор']:
                        # Faqat ob-havo kontekstida hisoblash
                        if any(w in text_lower for w in ['ob-havo', 'обҳаво', 'prognoz', 'прогноз', 'harorat', 'ҳарорат', 'gradus', 'градус']):
                            score += 1
                            matched_keywords.append(keyword_lower)
                    else:
                        score += 1
                        matched_keywords.append(keyword_lower)
            else:
                # YANGI: "havo" so'zini faqat ob-havo kontekstida hisoblash
                if keyword_lower == 'havo' or keyword_lower == 'ҳаво':
                    # Faqat ob-havo kontekstida hisoblash
                    if any(w in text_lower for w in ['ob-havo', 'обҳаво', 'prognoz', 'прогноз', 'harorat', 'ҳарорат']):
                        score += 1
                        matched_keywords.append(keyword_lower)
                else:
                    # Oddiy keyword matching
                    if keyword_lower in text_lower:
                        score += 1
                        matched_keywords.append(keyword_lower)
        
        if score > 0:
            scores[category] = score
            print(f"   📊 {category}: {score} ball ({', '.join(matched_keywords[:3])}...)")
    
    # Eng ko'p ball olgan kategoriya
    if scores:
        # Agar bir nechta kategoriya bir xil ball olsa - prioritet tartibida tanlash
        max_score = max(scores.values())
        candidates = [cat for cat, score in scores.items() if score == max_score]
        
        # YANGI: Ob-havo faqat aniq ob-havo yangiliklari uchun
        if 'obhavo' in candidates and len(candidates) > 1:
            # Agar boshqa kategoriyalar ham bor bo'lsa - ob-havoni olib tashlash
            candidates = [c for c in candidates if c != 'obhavo']
            print(f"   ⚖️ Ob-havo boshqa kategoriyalar bilan aralashgan - olib tashlandi")
        
        # Prioritet tartibi (muhimdan kam muhimga)
        priority_order = [
            'siyosat',      # Eng muhim
            'iqtisod',      # Iqtisodiy yangiliklar
            'jamiyat',      # Ijtimoiy yangiliklar (transport, ekologiya)
            'dunyo',        # Xalqaro
            'salomatlik',   # Salomatlik
            'texnologiya',  # Texnologiya
            'sport',        # Sport
            'obhavo'        # Ob-havo (eng oxirgi prioritet)
        ]
        
        # Prioritet bo'yicha birinchi topilgan kategoriyani qaytarish
        for priority_cat in priority_order:
            if priority_cat in candidates:
                if len(candidates) > 1:
                    print(f"   ⚖️ Bir nechta kategoriya ({candidates}) - prioritet: {priority_cat}")
                return priority_cat
        
        # Agar prioritetda yo'q bo'lsa - birinchisini qaytarish
        return candidates[0]
    
    # Agar hech qanday keyword topilmasa - matn tahlili
    # Raqamlar ko'p bo'lsa - ehtimol iqtisod
    if sum(c.isdigit() for c in text) > len(text) * 0.1:
        print(f"   🔢 Ko'p raqamlar - ehtimol iqtisod")
        return 'iqtisod'
    
    # Uzun matn (> 500 belgi) - ehtimol muhim yangilik
    if len(text) > 500:
        print(f"   📝 Uzun matn - jamiyat kategoriyasi")
        return 'jamiyat'
    
    # Hech qanday kategoriya topilmasa - None
    print(f"   ❌ Kategoriya topilmadi")
    return None

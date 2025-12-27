import os
from dotenv import load_dotenv

load_dotenv()

# Telegram API credentials (user account uchun - Telethon)
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE = os.getenv('PHONE')

# Bot token (user bilan ishlash uchun)
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Database
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///news_bot.db')

# Admin username (statistika ko'rish uchun)
ADMIN_USERNAME = 'Murodjon_PM'

# Kuzatiladigan kanallar (to'g'ri username lar)
CHANNELS_TO_MONITOR = [
    '@kunuz',  # Kun.uz
    '@yangiliklar331',
]

# Kategoriyalar va kalit so'zlar (kengaytirilgan + kirill)
CATEGORIES = {
    'siyosat': [
        # Lotin
        'prezident', 'parlament', 'saylov', 'hukumat', 'vazir', 'qonun', 'davlat', 
        'hokimiyat', 'senat', 'oliy majlis', 'deputat', 'farmon', 'qaror', 'lavozim',
        'ishdan olindi', 'tayinlandi', 'vazirlik', 'hokimlik',
        # Kirill
        'президент', 'парламент', 'сайлов', 'ҳукумат', 'вазир', 'қонун', 'давлат',
        'ҳокимият', 'сенат', 'олий мажлис', 'депутат', 'фармон', 'қарор', 'лавозим',
        'ишдан олинди', 'тайинланди', 'вазирлик', 'ҳокимлик'
    ],
    'iqtisod': [
        # Lotin
        'dollar', 'narx', 'bozor', 'bank', 'investitsiya', 'biznes', 'iqtisodiyot', 
        'savdo', 'valyuta', 'kurs', 'pul', 'moliya', 'soliq', 'byudjet',
        'ish haqi', 'ish haq', 'maosh', 'daromad', 'o\'sish', 'kamayish',
        'real', 'nominal', 'foiz', 'statistika', 'iqtisod',
        # Kirill
        'доллар', 'нарх', 'бозор', 'банк', 'инвестиция', 'бизнес', 'иқтисодиёт',
        'савдо', 'валюта', 'курс', 'пул', 'молия', 'солиқ', 'бюджет',
        'иш ҳақи', 'иш ҳақ', 'маош', 'даромад', 'ўсиш', 'камайиш',
        'реал', 'номинал', 'фоиз', 'статистика', 'иқтисод'
    ],
    'jamiyat': [
        # Lotin
        'ta\'lim', 'madaniyat', 'aholi', 'ijtimoiy', 'jamiyat', 'xalq', 
        'maktab', 'universitet', 'o\'quvchi', 'talaba', 'o\'qituvchi',
        'imtihon', 'test', 'grant', 'stipendiya', 'ta\'lim tizimi',
        'maktab', 'bog\'cha', 'kollej', 'litsey', 'akademiya',
        'festival', 'konsert', 'teatr', 'kino', 'san\'at', 'rasm',
        'musiqa', 'she\'r', 'adabiyat', 'kitob', 'kutubxona',
        # Transport va ekologiya
        'transport', 'avtomobil', 'mashina', 'yo\'l', 'yo\'lovchi', 'haydovchi',
        'avtobus', 'metro', 'tramvay', 'taksi', 'yuk', 'yuk mashinasi',
        'avtotransport', 'yo\'l-transport', 'hodisa', 'baxtsiz hodisa',
        'ekologiya', 'atrof-muhit', 'tabiat', 'iflos', 'toza', 'havo',
        'ekostiker', 'stiker', 'raqam', 'davlat raqami', 'texnik ko\'rik',
        'guvohnoma', 'haydovchilik guvohnomasi', 'prava', 'jarima',
        'yo\'l qoidalari', 'yo\'l belgisi', 'svetofor', 'piyoda',
        # Dayjest va umumiy
        'dayjest', 'hafta', 'haftalik', 'xulosa', 'sharh', 'tahlil',
        'ko\'rib chiqish', 'umumiy', 'turli', 'har xil', 'aralash',
        'ortda qolayotgan', 'o\'tgan hafta', 'o\'tgan kun',
        # Kirill
        'таълим', 'маданият', 'аҳоли', 'ижтимоий', 'жамият', 'халқ',
        'мактаб', 'университет', 'ўқувчи', 'талаба', 'ўқитувчи',
        'имтиҳон', 'тест', 'грант', 'стипендия', 'таълим тизими',
        'боғча', 'коллеж', 'лицей', 'академия',
        'фестивал', 'концерт', 'театр', 'кино', 'санъат', 'расм',
        'мусиқа', 'шеър', 'адабиёт', 'китоб', 'кутубхона',
        # Transport va ekologiya (kirill)
        'транспорт', 'автомобил', 'машина', 'йўл', 'йўловчи', 'ҳайдовчи',
        'автобус', 'метро', 'трамвай', 'такси', 'юк', 'юк машинаси',
        'автотранспорт', 'йўл-транспорт', 'ҳодиса', 'бахтсиз ҳодиса',
        'экология', 'атроф-муҳит', 'табиат', 'ифлос', 'тоза', 'ҳаво',
        'экостикер', 'стикер', 'рақам', 'давлат рақами', 'техник кўрик',
        'гувоҳнома', 'ҳайдовчилик гувоҳномаси', 'права', 'жарима',
        'йўл қоидалари', 'йўл белгиси', 'светофор', 'пиёда',
        # Dayjest va umumiy (kirill)
        'дайжест', 'ҳафта', 'ҳафталик', 'хулоса', 'шарҳ', 'таҳлил'
    ],
    'sport': [
        # Lotin
        'futbol', 'o\'yin', 'jamoa', 'chempion', 'liga', 'kubok', 'o\'yinchi',
        'murabbiy', 'stadion', 'gol', 'tennis', 'boks', 'kurash', 'basketbol',
        'voleybol', 'olimpiada', 'medal', 'sport', 'turnir', 'match', 'g\'alaba',
        'mag\'lubiyat', 'durang', 'final', 'yarim final', 'pley-off', 'transfer',
        'kontrak', 'jazo', 'sariq kartochka', 'qizil kartochka', 'penalti',
        # Kirill
        'футбол', 'ўйин', 'жамоа', 'чемпион', 'лига', 'кубок', 'ўйинчи',
        'мураббий', 'стадион', 'гол', 'теннис', 'бокс', 'кураш', 'баскетбол',
        'волейбол', 'олимпиада', 'медал', 'спорт', 'турнир', 'матч', 'ғалаба',
        'мағлубият', 'дуранг', 'финал', 'ярим финал', 'плей-офф', 'трансфер',
        'контракт', 'жазо', 'сариқ карточка', 'қизил карточка', 'пеналти',
        # Inglizcha
        'football', 'soccer', 'basketball', 'tennis', 'boxing', 'match', 'goal',
        'champion', 'league', 'cup', 'player', 'coach', 'stadium', 'win', 'lose'
    ],
    'texnologiya': [
        'apple', 'google', 'iphone', 'dastur', 'AI', 'sun\'iy intellekt', 
        'texnologiya', 'internet', 'telefon', 'kompyuter', 'android',
        'дастур', 'сунъий интеллект', 'технология', 'интернет', 'телефон', 'компьютер'
    ],
    'dunyo': [
        'xalqaro', 'mamlakatlar', 'urush', 'tinchlik', 'jahon', 'dunyo', 
        'aqsh', 'rossiya', 'xitoy', 'yevropa',
        'халқаро', 'мамлакатлар', 'уруш', 'тинчлик', 'жаҳон', 'дунё',
        'aqsh', 'россия', 'хитой', 'европа'
    ],
    'salomatlik': [
        'kasallik', 'shifokor', 'bemor', 'shifoxona', 'salomatlik', 'tibbiyot', 
        'dori', 'homila', 'tuxum', 'ovqat', 'parhez', 'vitamin',
        'касаллик', 'шифокор', 'бемор', 'шифохона', 'саломатлик', 'тиббиёт',
        'дори', 'ҳомила', 'тухум', 'овқат', 'парҳез', 'витамин'
    ],
    'obhavo': [
        # Lotin
        'ob-havo', 'obhavo', 'havo', 'harorat', 'yomg\'ir', 'qor', 'shamol',
        'bulut', 'quyosh', 'sovuq', 'issiq', 'nam', 'prognoz', 'iqlim',
        'daraja', 'gradus', 'celsius', 'tuman', 'yog\'in', 'chang', 'bo\'ron',
        # Kirill
        'об-ҳаво', 'обҳаво', 'ҳаво', 'ҳарорат', 'ёмғир', 'қор', 'шамол',
        'булут', 'қуёш', 'совуқ', 'иссиқ', 'нам', 'прогноз', 'иқлим',
        'даража', 'градус', 'цельсий', 'туман', 'ёғин', 'чанг', 'бўрон',
        # Inglizcha
        'weather', 'temperature', 'rain', 'snow', 'wind', 'forecast',
        'celsius', 'degree', 'cloud', 'sun', 'cold', 'hot', 'humidity',
        # Ruscha
        'погода', 'температура', 'дождь', 'снег', 'ветер', 'прогноз',
        'градус', 'облако', 'солнце', 'холод', 'жара'
    ]
}

# OpenAI API (agar ishlatmoqchi bo'lsangiz)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Trial davri (kunlarda)
TRIAL_DAYS = 7

# Obuna tariflar
SUBSCRIPTION_PLANS = {
    'basic': {
        'name': 'Basic',
        'price': 7000,
        'duration_days': 30,
        'emoji': '📦',
        'category_limit': 3  # 3 ta kategoriya
    },
    'premium': {
        'name': 'Premium',
        'price': 15000,
        'duration_days': 30,
        'emoji': '⭐',
        'category_limit': None  # Cheksiz
    },}
"""Fixed lookup tables used by the engine.

Every name is stored as an (English, Hindi) pair so the website and the PDF
can show either language without translating anything at run time.
"""

NAK_SPAN = 360 / 27          # one nakshatra = 13 deg 20 min
PADA_SPAN = NAK_SPAN / 4     # one pada = 3 deg 20 min

SIGNS = [
    ("Aries", "मेष"), ("Taurus", "वृषभ"), ("Gemini", "मिथुन"), ("Cancer", "कर्क"),
    ("Leo", "सिंह"), ("Virgo", "कन्या"), ("Libra", "तुला"), ("Scorpio", "वृश्चिक"),
    ("Sagittarius", "धनु"), ("Capricorn", "मकर"), ("Aquarius", "कुंभ"), ("Pisces", "मीन"),
]

# Lord of each sign, Aries first
SIGN_LORDS = [
    "mars", "venus", "mercury", "moon", "sun", "mercury",
    "venus", "mars", "jupiter", "saturn", "saturn", "jupiter",
]

PLANETS = {
    "sun": ("Sun", "सूर्य"), "moon": ("Moon", "चन्द्र"), "mars": ("Mars", "मंगल"),
    "mercury": ("Mercury", "बुध"), "jupiter": ("Jupiter", "गुरु"), "venus": ("Venus", "शुक्र"),
    "saturn": ("Saturn", "शनि"), "rahu": ("Rahu", "राहु"), "ketu": ("Ketu", "केतु"),
}
PLANET_KEYS = list(PLANETS)

NAKSHATRAS = [
    ("Ashwini", "अश्विनी"), ("Bharani", "भरणी"), ("Krittika", "कृत्तिका"),
    ("Rohini", "रोहिणी"), ("Mrigashira", "मृगशिरा"), ("Ardra", "आर्द्रा"),
    ("Punarvasu", "पुनर्वसु"), ("Pushya", "पुष्य"), ("Ashlesha", "आश्लेषा"),
    ("Magha", "मघा"), ("Purva Phalguni", "पूर्वा फाल्गुनी"), ("Uttara Phalguni", "उत्तरा फाल्गुनी"),
    ("Hasta", "हस्त"), ("Chitra", "चित्रा"), ("Swati", "स्वाती"),
    ("Vishakha", "विशाखा"), ("Anuradha", "अनुराधा"), ("Jyeshtha", "ज्येष्ठा"),
    ("Mula", "मूल"), ("Purva Ashadha", "पूर्वाषाढ़ा"), ("Uttara Ashadha", "उत्तराषाढ़ा"),
    ("Shravana", "श्रवण"), ("Dhanishta", "धनिष्ठा"), ("Shatabhisha", "शतभिषा"),
    ("Purva Bhadrapada", "पूर्वा भाद्रपद"), ("Uttara Bhadrapada", "उत्तरा भाद्रपद"), ("Revati", "रेवती"),
]

# Nakshatra indexes (0-based) that are Gandmool: Ashwini, Ashlesha, Magha, Jyeshtha, Mula, Revati
GANDMOOL_NAKSHATRAS = {0, 8, 9, 17, 18, 26}

# Name syllable for each nakshatra pada (4 per nakshatra, Ashwini first)
NAAM_AKSHAR = [
    [("Chu", "चू"), ("Che", "चे"), ("Cho", "चो"), ("La", "ला")],
    [("Li", "ली"), ("Lu", "लू"), ("Le", "ले"), ("Lo", "लो")],
    [("A", "अ"), ("I", "ई"), ("U", "उ"), ("E", "ए")],
    [("O", "ओ"), ("Va", "वा"), ("Vi", "वी"), ("Vu", "वू")],
    [("Ve", "वे"), ("Vo", "वो"), ("Ka", "का"), ("Ki", "की")],
    [("Ku", "कू"), ("Gha", "घ"), ("Nga", "ङ"), ("Chha", "छ")],
    [("Ke", "के"), ("Ko", "को"), ("Ha", "हा"), ("Hi", "ही")],
    [("Hu", "हू"), ("He", "हे"), ("Ho", "हो"), ("Da", "डा")],
    [("Di", "डी"), ("Du", "डू"), ("De", "डे"), ("Do", "डो")],
    [("Ma", "मा"), ("Mi", "मी"), ("Mu", "मू"), ("Me", "मे")],
    [("Mo", "मो"), ("Ta", "टा"), ("Ti", "टी"), ("Tu", "टू")],
    [("Te", "टे"), ("To", "टो"), ("Pa", "पा"), ("Pi", "पी")],
    [("Pu", "पू"), ("Sha", "ष"), ("Na", "ण"), ("Tha", "ठ")],
    [("Pe", "पे"), ("Po", "पो"), ("Ra", "रा"), ("Ri", "री")],
    [("Ru", "रू"), ("Re", "रे"), ("Ro", "रो"), ("Ta", "ता")],
    [("Ti", "ती"), ("Tu", "तू"), ("Te", "ते"), ("To", "तो")],
    [("Na", "ना"), ("Ni", "नी"), ("Nu", "नू"), ("Ne", "ने")],
    [("No", "नो"), ("Ya", "या"), ("Yi", "यी"), ("Yu", "यू")],
    [("Ye", "ये"), ("Yo", "यो"), ("Bha", "भा"), ("Bhi", "भी")],
    [("Bhu", "भू"), ("Dha", "धा"), ("Pha", "फा"), ("Dha", "ढा")],
    [("Bhe", "भे"), ("Bho", "भो"), ("Ja", "जा"), ("Ji", "जी")],
    [("Khi", "खी"), ("Khu", "खू"), ("Khe", "खे"), ("Kho", "खो")],
    [("Ga", "गा"), ("Gi", "गी"), ("Gu", "गू"), ("Ge", "गे")],
    [("Go", "गो"), ("Sa", "सा"), ("Si", "सी"), ("Su", "सू")],
    [("Se", "से"), ("So", "सो"), ("Da", "दा"), ("Di", "दी")],
    [("Du", "दू"), ("Tha", "थ"), ("Jha", "झ"), ("Yna", "ञ")],
    [("De", "दे"), ("Do", "दो"), ("Cha", "चा"), ("Chi", "ची")],
]

# First 14 tithi names; the 15th is Purnima (bright half) or Amavasya (dark half)
TITHIS = [
    ("Pratipada", "प्रतिपदा"), ("Dwitiya", "द्वितीया"), ("Tritiya", "तृतीया"),
    ("Chaturthi", "चतुर्थी"), ("Panchami", "पंचमी"), ("Shashthi", "षष्ठी"),
    ("Saptami", "सप्तमी"), ("Ashtami", "अष्टमी"), ("Navami", "नवमी"),
    ("Dashami", "दशमी"), ("Ekadashi", "एकादशी"), ("Dwadashi", "द्वादशी"),
    ("Trayodashi", "त्रयोदशी"), ("Chaturdashi", "चतुर्दशी"),
]
PURNIMA = ("Purnima", "पूर्णिमा")
AMAVASYA = ("Amavasya", "अमावस्या")
PAKSHAS = [("Shukla", "शुक्ल"), ("Krishna", "कृष्ण")]

YOGAS = [
    ("Vishkambha", "विष्कम्भ"), ("Priti", "प्रीति"), ("Ayushman", "आयुष्मान"),
    ("Saubhagya", "सौभाग्य"), ("Shobhana", "शोभन"), ("Atiganda", "अतिगण्ड"),
    ("Sukarma", "सुकर्मा"), ("Dhriti", "धृति"), ("Shula", "शूल"),
    ("Ganda", "गण्ड"), ("Vriddhi", "वृद्धि"), ("Dhruva", "ध्रुव"),
    ("Vyaghata", "व्याघात"), ("Harshana", "हर्षण"), ("Vajra", "वज्र"),
    ("Siddhi", "सिद्धि"), ("Vyatipata", "व्यतीपात"), ("Variyan", "वरीयान"),
    ("Parigha", "परिघ"), ("Shiva", "शिव"), ("Siddha", "सिद्ध"),
    ("Sadhya", "साध्य"), ("Shubha", "शुभ"), ("Shukla", "शुक्ल"),
    ("Brahma", "ब्रह्म"), ("Indra", "इन्द्र"), ("Vaidhriti", "वैधृति"),
]

# 7 repeating karanas, then the 4 fixed ones
KARANAS_MOVABLE = [
    ("Bava", "बव"), ("Balava", "बालव"), ("Kaulava", "कौलव"), ("Taitila", "तैतिल"),
    ("Gara", "गर"), ("Vanija", "वणिज"), ("Vishti", "विष्टि"),
]
KARANA_KIMSTUGHNA = ("Kimstughna", "किंस्तुघ्न")
KARANAS_FIXED_END = [("Shakuni", "शकुनि"), ("Chatushpada", "चतुष्पाद"), ("Naga", "नाग")]

# Index = Python weekday (Monday = 0). Third item is the planet that rules the day.
WEEKDAYS = [
    ("Monday", "सोमवार", "moon"), ("Tuesday", "मंगलवार", "mars"),
    ("Wednesday", "बुधवार", "mercury"), ("Thursday", "गुरुवार", "jupiter"),
    ("Friday", "शुक्रवार", "venus"), ("Saturday", "शनिवार", "saturn"),
    ("Sunday", "रविवार", "sun"),
]

# Order in which planets rule the hours (hora) of a day
HORA_SEQUENCE = ["sun", "venus", "mercury", "moon", "saturn", "jupiter", "mars"]

# Which eighth of the daytime is Rahu Kaal (1-based), index = Python weekday
RAHU_KAAL_PART = [2, 7, 5, 6, 4, 3, 8]

LUNAR_MONTHS = [
    ("Chaitra", "चैत्र"), ("Vaishakha", "वैशाख"), ("Jyeshtha", "ज्येष्ठ"),
    ("Ashadha", "आषाढ़"), ("Shravana", "श्रावण"), ("Bhadrapada", "भाद्रपद"),
    ("Ashwin", "आश्विन"), ("Kartik", "कार्तिक"), ("Margashirsha", "मार्गशीर्ष"),
    ("Pausha", "पौष"), ("Magha", "माघ"), ("Phalguna", "फाल्गुन"),
]

RITUS = [
    ("Vasant", "वसंत"), ("Grishma", "ग्रीष्म"), ("Varsha", "वर्षा"),
    ("Sharad", "शरद"), ("Hemant", "हेमंत"), ("Shishir", "शिशिर"),
]

AYANAS = [("Uttarayana", "उत्तरायण"), ("Dakshinayana", "दक्षिणायन")]

# 60-year cycle of year names, Prabhava first
SAMVATSARAS = [
    ("Prabhava", "प्रभव"), ("Vibhava", "विभव"), ("Shukla", "शुक्ल"), ("Pramoda", "प्रमोद"),
    ("Prajapati", "प्रजापति"), ("Angirasa", "अंगिरा"), ("Shrimukha", "श्रीमुख"), ("Bhava", "भाव"),
    ("Yuva", "युवा"), ("Dhata", "धाता"), ("Ishvara", "ईश्वर"), ("Bahudhanya", "बहुधान्य"),
    ("Pramathi", "प्रमाथी"), ("Vikrama", "विक्रम"), ("Vrisha", "वृष"), ("Chitrabhanu", "चित्रभानु"),
    ("Subhanu", "सुभानु"), ("Tarana", "तारण"), ("Parthiva", "पार्थिव"), ("Vyaya", "व्यय"),
    ("Sarvajit", "सर्वजित्"), ("Sarvadhari", "सर्वधारी"), ("Virodhi", "विरोधी"), ("Vikriti", "विकृति"),
    ("Khara", "खर"), ("Nandana", "नंदन"), ("Vijaya", "विजय"), ("Jaya", "जय"),
    ("Manmatha", "मन्मथ"), ("Durmukha", "दुर्मुख"), ("Hevilambi", "हेविलम्बी"), ("Vilambi", "विलम्बी"),
    ("Vikari", "विकारी"), ("Sharvari", "शार्वरी"), ("Plava", "प्लव"), ("Shubhakrit", "शुभकृत्"),
    ("Shobhakrit", "शोभकृत्"), ("Krodhi", "क्रोधी"), ("Vishvavasu", "विश्वावसु"), ("Parabhava", "पराभव"),
    ("Plavanga", "प्लवंग"), ("Kilaka", "कीलक"), ("Saumya", "सौम्य"), ("Sadharana", "साधारण"),
    ("Virodhakrit", "विरोधकृत्"), ("Paridhavi", "परिधावी"), ("Pramadi", "प्रमादी"), ("Ananda", "आनंद"),
    ("Rakshasa", "राक्षस"), ("Nala", "नल"), ("Pingala", "पिंगल"), ("Kalayukta", "कालयुक्त"),
    ("Siddharthi", "सिद्धार्थी"), ("Raudra", "रौद्र"), ("Durmati", "दुर्मति"), ("Dundubhi", "दुन्दुभि"),
    ("Rudhirodgari", "रुधिरोद्गारी"), ("Raktakshi", "रक्ताक्षी"), ("Krodhana", "क्रोधन"), ("Akshaya", "अक्षय"),
]

# ---- Dignity (strength by sign) ----
EXALTATION_SIGN = {
    "sun": 0, "moon": 1, "mars": 9, "mercury": 5, "jupiter": 3, "venus": 11, "saturn": 6,
}
# planet -> (sign, from degree, to degree)
MOOLATRIKONA = {
    "sun": (4, 0, 20), "moon": (1, 3, 30), "mars": (0, 0, 12), "mercury": (5, 15, 20),
    "jupiter": (8, 0, 10), "venus": (6, 0, 15), "saturn": (10, 0, 20),
}

# ---- Vimshottari dasha ----
DASHA_ORDER = ["ketu", "venus", "sun", "moon", "mars", "rahu", "jupiter", "saturn", "mercury"]
DASHA_YEARS = {
    "ketu": 7, "venus": 20, "sun": 6, "moon": 10, "mars": 7,
    "rahu": 18, "jupiter": 16, "saturn": 19, "mercury": 17,
}
DASHA_YEAR_DAYS = 365.25

# ---- Avakahada Chakra ----
ELEMENTS = [("Fire", "अग्नि"), ("Earth", "पृथ्वी"), ("Air", "वायु"), ("Water", "जल")]
# Varna follows the element of the Moon sign (fire, earth, air, water)
VARNAS = [("Kshatriya", "क्षत्रिय"), ("Vaishya", "वैश्य"), ("Shudra", "शूद्र"), ("Brahmin", "ब्राह्मण")]

VASHYAS = {
    "chatushpada": ("Chatushpada", "चतुष्पद"), "manav": ("Manav", "मानव"),
    "jalachar": ("Jalachar", "जलचर"), "vanchar": ("Vanchar", "वनचर"), "keet": ("Keet", "कीट"),
}

YONIS = {
    "ashwa": ("Ashwa (Horse)", "अश्व"), "gaja": ("Gaja (Elephant)", "गज"),
    "mesha": ("Mesha (Sheep)", "मेष"), "sarpa": ("Sarpa (Serpent)", "सर्प"),
    "shwan": ("Shwan (Dog)", "श्वान"), "marjar": ("Marjar (Cat)", "मार्जार"),
    "mushak": ("Mushak (Rat)", "मूषक"), "gau": ("Gau (Cow)", "गौ"),
    "mahisha": ("Mahisha (Buffalo)", "महिष"), "vyaghra": ("Vyaghra (Tiger)", "व्याघ्र"),
    "mriga": ("Mriga (Deer)", "मृग"), "vanar": ("Vanar (Monkey)", "वानर"),
    "nakul": ("Nakul (Mongoose)", "नकुल"), "simha": ("Simha (Lion)", "सिंह"),
}
# Yoni of each nakshatra, Ashwini first
NAKSHATRA_YONI = [
    "ashwa", "gaja", "mesha", "sarpa", "sarpa", "shwan", "marjar", "mesha", "marjar",
    "mushak", "mushak", "gau", "mahisha", "vyaghra", "mahisha", "vyaghra", "mriga", "mriga",
    "shwan", "vanar", "nakul", "vanar", "simha", "ashwa", "simha", "gau", "gaja",
]

GANAS = [("Deva", "देव"), ("Manushya", "मनुष्य"), ("Rakshasa", "राक्षस")]
# Gana of each nakshatra (0 Deva, 1 Manushya, 2 Rakshasa), Ashwini first
NAKSHATRA_GANA = [
    0, 1, 2, 1, 0, 1, 0, 0, 2,
    2, 1, 1, 0, 2, 0, 2, 0, 2,
    2, 1, 1, 0, 2, 2, 1, 1, 0,
]

NADIS = [("Adi", "आदि"), ("Madhya", "मध्य"), ("Antya", "अन्त्य")]
# Nadi repeats in this pattern across the 27 nakshatras
NADI_PATTERN = [0, 1, 2, 2, 1, 0]

# Paya is taken from the Moon's house counted from the Lagna
PAYAS = {
    "gold": ("Swarna (Gold)", "स्वर्ण"), "silver": ("Rajat (Silver)", "रजत"),
    "copper": ("Tamra (Copper)", "ताम्र"), "iron": ("Loha (Iron)", "लौह"),
}
PAYA_BY_MOON_HOUSE = {
    1: "gold", 6: "gold", 11: "gold",
    2: "silver", 5: "silver", 9: "silver",
    3: "copper", 7: "copper", 10: "copper",
    4: "iron", 8: "iron", 12: "iron",
}

# Jaimini Chara Karakas (7-planet scheme), highest degree first
CHARA_KARAKAS = [
    ("atmakaraka", "Atmakaraka"), ("amatyakaraka", "Amatyakaraka"),
    ("bhratrikaraka", "Bhratrikaraka"), ("matrikaraka", "Matrikaraka"),
    ("putrakaraka", "Putrakaraka"), ("gnatikaraka", "Gnatikaraka"),
    ("darakaraka", "Darakaraka"),
]


def named(pair, index=None):
    """Turn an (English, Hindi) pair into the dictionary shape used in the output."""
    out = {"en": pair[0], "hi": pair[1]}
    if index is not None:
        out["index"] = index
    return out

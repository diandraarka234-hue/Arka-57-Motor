import re
import json
import random
import urllib.parse
import webbrowser
from pathlib import Path
from rapidfuzz import process, fuzz

# =====================
# FILE PATH
# =====================
BASE_DIR = Path(__file__).resolve().parent
FAQ_FILE = BASE_DIR / "learned_faq.json"

# =====================
# OWNER & MAPS CONFIG
# =====================
OWNER_WA = "62895417804158"  # Format internasional tanpa +
MAPS_LINK = "https://maps.app.goo.gl/nWKtHJc3Wbjh5i5z9?g_st=aw"

# =====================
# BENGKEL INFO
# =====================
BENGKEL = {
    "nama": "Arka 57 Motor",
    "kota": "Tegal",
    "jam": "07:00 - 17:00",
    "wa": "0895-4178-04158"
}

# =====================
# FRIENDLY TEMPLATES
# =====================
GREETINGS = [
    "Halo! 😊 Selamat datang di Arka 57 Motor.",
    "Hai! 👋 Terima kasih sudah menghubungi Arka 57 Motor.",
    "Selamat datang! 😊 Senang bisa membantu Anda di Arka 57 Motor."
]

CLOSINGS = [
    "Ada lagi yang bisa saya bantu? 😊",
    "Silakan tanyakan jika ada yang ingin diketahui ya! 🙏",
    "Saya siap membantu kapan saja. 😊"
]

THANKS = [
    "Terima kasih sudah menghubungi kami 🙏",
    "Terima kasih ya, kami senang bisa membantu 😊",
]

# =====================
# TOXIC FILTER
# =====================
BAD_WORDS = [
    "anjing", "bangsat", "babi", "kontol", "memek", "ngentot",
    "tolol", "goblok", "brengsek", "kampret",
    "fuck", "shit", "asshole"
]

POLITE_WARNINGS = [
    "Maaf ya 😊 kami berusaha menggunakan bahasa yang sopan agar bisa membantu dengan nyaman. Silakan sampaikan pertanyaan Anda dengan bahasa yang lebih baik 🙏",
    "Kami siap membantu Anda 😊 Mohon gunakan bahasa yang sopan agar komunikasi kita lebih nyaman ya 🙏",
    "Terima kasih sudah menghubungi kami 🙏 Agar kami bisa membantu dengan maksimal, mohon gunakan bahasa yang sopan ya 😊"
]

# =====================
# DEFAULT FAQ
# =====================
DEFAULT_FAQ = {
    "harga servis motor": "Harga servis motor mulai dari Rp50.000 tergantung jenis servis dan kondisi motor.",
    "jam buka bengkel": f"Kami buka setiap hari dari jam {BENGKEL['jam']}.",
    "alamat bengkel": f"Kami berlokasi di kota {BENGKEL['kota']}.",
    "kontak bengkel": f"Silakan hubungi kami di WhatsApp {BENGKEL['wa']}.",
    "layanan bengkel": "Kami melayani servis ringan, servis berat, ganti oli, tune up, dan penjualan sparepart."
}

# =====================
# INTENTS
# =====================
INTENTS = {
    "harga": {
        "patterns": ["harga", "biaya", "berapa", "tarif", "bayar", "hrg"],
        "response": "Untuk info harga, servis motor mulai dari Rp50.000. Servis apa yang Anda butuhkan?"
    },
    "jam": {
        "patterns": ["jam", "buka", "tutup", "operasional", "open", "close"],
        "response": f"Kami buka setiap hari dari jam {BENGKEL['jam']}."
    },
    "lokasi": {
        "patterns": ["alamat", "lokasi", "dimana", "maps", "arah"],
        "response": f"Lokasi kami berada di kota {BENGKEL['kota']}. Mau saya kirim link Google Maps?"
    },
    "kontak": {
        "patterns": ["kontak", "whatsapp", "nomor", "telepon", "hubungi", "wa"],
        "response": f"Silakan hubungi kami melalui WhatsApp di {BENGKEL['wa']}."
    },
    "layanan": {
        "patterns": ["servis", "service", "oli", "tune up", "perbaikan", "jasa"],
        "response": "Kami melayani servis ringan, servis berat, ganti oli, dan tune up. Mau saya bantu buatkan booking?"
    }
}

# =====================
# USER SESSION
# =====================
USER_SESSION = {
    "name": None,
    "last_topic": None,
    "booking": None
}

# =====================
# FILE HANDLING
# =====================
def load_learned_faq():
    if not FAQ_FILE.exists():
        FAQ_FILE.write_text(json.dumps({}, indent=2))
        return {}
    try:
        return json.loads(FAQ_FILE.read_text())
    except:
        return {}

def save_learned_faq(data):
    FAQ_FILE.write_text(json.dumps(data, indent=2))

# =====================
# UTIL
# =====================
def clean_text(text):
    return re.sub(r"[^a-zA-Z0-9\s]", "", text.lower()).strip()

def detect_name(text):
    patterns = [
        r"nama saya ([a-zA-Z]+)",
        r"saya ([a-zA-Z]+)",
        r"aku ([a-zA-Z]+)",
        r"panggil saya ([a-zA-Z]+)"
    ]
    for p in patterns:
        match = re.search(p, text.lower())
        if match:
            return match.group(1).capitalize()
    return None

def friendly_prefix():
    if USER_SESSION["name"]:
        return f"{USER_SESSION['name']}, "
    return ""

def friendly_suffix():
    return "\n\n" + random.choice(CLOSINGS)

def contains_bad_word(text):
    t = text.lower()
    for word in BAD_WORDS:
        if word in t:
            return True
    return False

# =====================
# WHATSAPP SENDER
# =====================
def send_whatsapp_to_owner(text):
    encoded = urllib.parse.quote(text)
    url = f"https://wa.me/{OWNER_WA}?text={encoded}"
    try:
        webbrowser.open(url)
    except:
        pass

# =====================
# FUZZY MATCH
# =====================
def fuzzy_intent_match(message, threshold=70):
    best = None
    best_score = 0
    for key, intent in INTENTS.items():
        for p in intent["patterns"]:
            score = fuzz.partial_ratio(message, p)
            if score > best_score:
                best_score = score
                best = key
    return best if best_score >= threshold else None

def fuzzy_faq_match(message, faq_data, threshold=70):
    if not faq_data:
        return None
    match = process.extractOne(list(faq_data.keys()), message, scorer=fuzz.token_sort_ratio)
    if match and match[1] >= threshold:
        return faq_data[match[0]]
    return None

# =====================
# BOOKING FLOW
# =====================
def handle_booking(msg):
    b = USER_SESSION["booking"]

    if b is None:
        USER_SESSION["booking"] = {}
        return "Baik 😊 saya bantu booking servis. Siapa nama Anda?"

    if "name" not in b:
        b["name"] = msg.title()
        return "Terima kasih! 🙏 Jenis motor apa? (contoh: Beat, Vario, Supra)"

    if "motor" not in b:
        b["motor"] = msg
        return "Apa keluhan atau jenis servis yang dibutuhkan?"

    if "keluhan" not in b:
        b["keluhan"] = msg
        return "Tanggal servis yang diinginkan? (contoh: 20 Januari)"

    if "tanggal" not in b:
        b["tanggal"] = msg
        return "Jam berapa Anda akan datang ke bengkel?"

    if "jam" not in b:
        b["jam"] = msg

        summary = (
            "📋 Booking Servis Baru\n\n"
            f"Nama: {b['name']}\n"
            f"Motor: {b['motor']}\n"
            f"Keluhan: {b['keluhan']}\n"
            f"Tanggal: {b['tanggal']}\n"
            f"Jam: {b['jam']}\n\n"
            f"Bengkel: {BENGKEL['nama']} - {BENGKEL['kota']}"
        )

        # Auto kirim ke WhatsApp Owner
        send_whatsapp_to_owner(summary)

        USER_SESSION["booking"] = None

        return (
            "📋 *Booking Servis Berhasil!* ✅\n\n"
            f"Nama: {b['name']}\n"
            f"Motor: {b['motor']}\n"
            f"Keluhan: {b['keluhan']}\n"
            f"Tanggal: {b['tanggal']}\n"
            f"Jam: {b['jam']}\n\n"
            "📍 *Lokasi Bengkel Kami:*\n"
            f"{MAPS_LINK}\n\n"
            "Detail booking Anda sudah kami kirim ke admin melalui WhatsApp.\n"
            "Kami tunggu kedatangannya ya 😊"
            + friendly_suffix()
        )

# =====================
# BOT ENGINE
# =====================
def get_bot_reply(message):
    raw = message
    msg = clean_text(message)

    learned_faq = load_learned_faq()
    combined_faq = {**DEFAULT_FAQ, **learned_faq}

    # 0. Toxic filter
    if contains_bad_word(message):
        return random.choice(POLITE_WARNINGS)

    # 1. Greeting
    if not USER_SESSION["name"] and msg in ["halo", "hai", "hello", "pagi", "siang", "malam"]:
        return random.choice(GREETINGS) + "\n\nAda yang bisa saya bantu hari ini? 😊"

    # 2. Booking mode aktif
    if USER_SESSION["booking"] is not None:
        return handle_booking(raw)

    # 3. Detect name
    name = detect_name(raw)
    if name:
        USER_SESSION["name"] = name
        return f"Senang bertemu dengan Anda, {name}! 😊 Ada yang bisa saya bantu hari ini?"

    # 4. Thank you
    if msg in ["terima kasih", "makasih", "thanks", "thx"]:
        return random.choice(THANKS) + friendly_suffix()

    # 5. Follow-up booking
    if msg in ["iya", "ya", "boleh", "ok", "siap"] and USER_SESSION["last_topic"] == "layanan":
        USER_SESSION["booking"] = None
        return "Siap 😊 saya bantu buatkan booking servis sekarang." + friendly_suffix()

    # 6. Intent detection
    intent = fuzzy_intent_match(msg)
    if intent:
        USER_SESSION["last_topic"] = intent
        return friendly_prefix() + INTENTS[intent]["response"] + friendly_suffix()

    # 7. FAQ fuzzy
    faq_answer = fuzzy_faq_match(msg, combined_faq)
    if faq_answer:
        return friendly_prefix() + faq_answer + friendly_suffix()

    # 8. Learn new question
    if msg and msg not in learned_faq:
        learned_faq[msg] = None
        save_learned_faq(learned_faq)

    # 9. Fallback
    return (
        random.choice(GREETINGS) + "\n\n"
        "Maaf ya, saya belum punya jawabannya saat ini 🙏\n"
        "Pertanyaan Anda sudah kami simpan agar admin bisa menambahkan jawaban.\n\n"
        f"Jika butuh cepat, silakan hubungi WhatsApp kami di {BENGKEL['wa']}."
        + friendly_suffix()
    )

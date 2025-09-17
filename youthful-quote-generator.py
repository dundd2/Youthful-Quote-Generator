import tkinter as tk
import random
import os
import copy
import webbrowser
from tkinter import simpledialog, messagebox, ttk, scrolledtext, filedialog
from collections import defaultdict, Counter
from datetime import datetime
from urllib.parse import quote_plus
import pyttsx3
import json
import requests
import sys
import base64
import platform
import unicodedata
import subprocess
from hashlib import sha256

# Optional: cryptography is used for encrypting exported favourites to avoid
# storing user data in clear text on disk. If not installed, export will fall
# back to plain text after warning the user.
try:
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    from cryptography.fernet import Fernet, InvalidToken
    CRYPTO_AVAILABLE = True
except Exception:
    CRYPTO_AVAILABLE = False

APP_VERSION = "v1.1"
BUILD_DATE = "17/09/2025"
GITHUB_URL = "https://github.com/dundd2"


quotes = {
    "Courage": [
        "We, in our youth, dare to pursue our dreams, even facing hardship, we still believe in ourselves.",
        "Don't be afraid of failure, for every setback is a step towards success.",
        "Having a brave heart, youth is our greatest asset.",
        "Youth is the time to chase dreams; don't be afraid of failures.",
        "The greatest courage is to be yourself in a world that wants you to be someone else.",
        "Face your fears with determination, for that's how heroes are made.",
        "Courage isn't about being fearless, it's about facing life despite your fears.",
        "Every brave attempt is an opportunity for growth.",
        "True courage comes from perseverance in the face of difficulties."
    ],
    "Friendship": [
        "Treasure friendships, for they are the most beautiful memories of youth.",
        "A good friendship is like a precious gem, worth cherishing with all our heart.",
        "Friends from our youth often become our lifelong companions.",
        "Friendship is the foundation of happiness; treasure your friends.",
        "True friends are like stars; you don't always see them, but you know they're always there.",
        "Friendship is about finding people who understand your weirdness.",
        "Friends are the family we choose for ourselves.",
        "Sincere friendship is youth's most beautiful gift.",
        "Understanding between friends is a resonance of souls."
    ],
    "Dreams": [
        "Youth is a poem, filled with courage and dreams, though time may gradually fade it.",
        "Even when life is tough, ideals can light the way forward.",
        "Every adventure in our youth is an exploration of the future.",
        "Dreams are the whispers of your soul; listen to them.",
        "Your dreams are the blueprints of your destiny.",
        "Chase your dreams until you catch them.",
        "Dreams are today's answers to tomorrow's questions.",
        "Dreams are the compass of the soul, guiding our direction forward.",
        "The pursuit of dreams is a journey of self-realization."
    ],
    "Love": [
        "Young love is like the rising sun, filled with hope and beauty.",
        "Even if we've been hurt, love is still worth pursuing.",
        "Love is the mark of youth, forever etched in our hearts.",
        "Love is the music of the heart; let it play.",
        "Love is not about finding the perfect person, but seeing an imperfect person perfectly.",
        "True love stories never have endings.",
        "Love is the poetry of the senses.",
        "Love is the most beautiful scenery of youth.",
        "True love needs no words, only sincerity."
    ],
    "Life": [
        "Life is not easy for everyone, but we must learn to enjoy every moment.",
        "Every challenge is an opportunity for growth.",
        "Young life is like a blank canvas, waiting for us to fill it.",
        "Life is a journey; embrace every twist and turn.",
        "Life is short, but it's wide enough to hold all your dreams.",
        "Every day is a new page in your life's story.",
        "Life is about creating yourself, not finding yourself.",
        "Life is like a song, let us sing our own melody.",
        "Life is like an adventure, full of surprises and challenges."
    ],
    "Growth": [
        "Every challenge you face is an opportunity for growth.",
        "Growth is painful, change is painful, but nothing is as painful as staying stuck.",
        "The only way to grow is to step out of your comfort zone."
    ],
    "Wisdom": [
        "Knowledge comes from learning, wisdom comes from living.",
        "The greatest wisdom is knowing you have more to learn.",
        "Wisdom is not about knowing everything, but understanding what matters."
    ],
    "Success": [
        "Success is not final, failure is not fatal: it is the courage to continue that counts.",
        "The road to success is always under construction.",
        "Success is walking from failure to failure with no loss of enthusiasm."
    ],
    "Happiness": [
        "Happiness is not something ready made. It comes from your own actions.",
        "The greatest happiness comes from the smallest moments.",
        "Choose happiness, choose to smile, choose to shine."
    ],
    "Inspiration": [
        "Inspiration exists, but it has to find you working.",
        "Let your light shine so bright that others can see their way out of the dark.",
        "Be the inspiration you wish to see in the world."
    ]
}

users = {}
user_quotes = defaultdict(list)
quote_ratings = defaultdict(list)
quote_comments = defaultdict(list)
custom_quotes = []
achievements = defaultdict(list)
favorite_quotes = defaultdict(list)
language_preferences = {}
reflection_entries = defaultdict(list)
user_goals = defaultdict(list)

language_options = [
    "English",
    "Spanish",
    "French",
    "Chinese (Simplified)"
]


def _safe_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = os.getenv("YQG_OPENAI_MODEL", os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"))
OPENAI_TIMEOUT = _safe_int(os.getenv("YQG_OPENAI_TIMEOUT"), 15)
OPENROUTER_API_URL = os.getenv("YQG_OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
OPENROUTER_MODEL = os.getenv("YQG_OPENROUTER_MODEL", os.getenv("OPENROUTER_MODEL", "openrouter/openai/gpt-3.5-turbo"))
OPENROUTER_TIMEOUT = _safe_int(os.getenv("YQG_OPENROUTER_TIMEOUT"), OPENAI_TIMEOUT)
GEMINI_API_URL = os.getenv("YQG_GEMINI_URL", "https://generativelanguage.googleapis.com/v1beta")
GEMINI_MODEL = os.getenv("YQG_GEMINI_MODEL", os.getenv("GEMINI_MODEL", "gemini-pro"))
GEMINI_TIMEOUT = _safe_int(os.getenv("YQG_GEMINI_TIMEOUT"), OPENAI_TIMEOUT)
SUPPORTED_AI_PROVIDERS = ("openai", "openrouter", "gemini")
AI_PROVIDER_NAMES = {"openai": "OpenAI", "openrouter": "OpenRouter", "gemini": "Gemini"}
DEFAULT_AI_PROVIDER = os.getenv("YQG_AI_PROVIDER", "openai")


def _normalise_ai_provider(provider):
    provider = (provider or "openai").strip().lower()
    if provider not in SUPPORTED_AI_PROVIDERS:
        return "openai"
    return provider



def _build_default_ai_settings():
    default_provider = _normalise_ai_provider(DEFAULT_AI_PROVIDER)
    return {
        "provider": default_provider,
        "openai": {
            "api_key": (os.getenv("OPENAI_API_KEY") or "").strip(),
            "model": OPENAI_MODEL,
            "endpoint": OPENAI_API_URL,
            "timeout": OPENAI_TIMEOUT,
        },
        "openrouter": {
            "api_key": (os.getenv("OPENROUTER_API_KEY") or "").strip(),
            "model": OPENROUTER_MODEL,
            "endpoint": OPENROUTER_API_URL,
            "timeout": OPENROUTER_TIMEOUT,
            "app_url": os.getenv("OPENROUTER_APP_URL", ""),
            "app_name": os.getenv("OPENROUTER_APP_NAME", "Youthful Quote Generator"),
        },
        "gemini": {
            "api_key": (os.getenv("GEMINI_API_KEY") or "").strip(),
            "model": GEMINI_MODEL,
            "endpoint": GEMINI_API_URL,
            "timeout": GEMINI_TIMEOUT,
        },
    }



def _merge_ai_settings(overrides):
    base = copy.deepcopy(_build_default_ai_settings())
    if isinstance(overrides, dict):
        provider = overrides.get("provider")
        if provider:
            base["provider"] = _normalise_ai_provider(provider)
        for key in ("openai", "openrouter", "gemini"):
            values = overrides.get(key)
            if isinstance(values, dict):
                for inner_key, inner_value in values.items():
                    if inner_value is None:
                        continue
                    if inner_key == "api_key":
                        base[key][inner_key] = (inner_value or "").strip()
                    else:
                        base[key][inner_key] = inner_value
    return base



ai_settings = _build_default_ai_settings()

quote_translations = {
    "Spanish": {
        "We, in our youth, dare to pursue our dreams, even facing hardship, we still believe in ourselves.": "En nuestra juventud nos atrevemos a perseguir nuestros sueños; incluso frente a las dificultades seguimos creyendo en nosotros mismos.",
        "Don't be afraid of failure, for every setback is a step towards success.": "No temas al fracaso, porque cada tropiezo es un paso hacia el éxito.",
        "Having a brave heart, youth is our greatest asset.": "Con un corazón valiente, la juventud es nuestro mayor tesoro.",
        "Treasure friendships, for they are the most beautiful memories of youth.": "Atesora las amistades, porque son los recuerdos más bellos de la juventud.",
        "Friends are the family we choose for ourselves.": "Los amigos son la familia que elegimos para nosotros mismos.",
        "Dreams are the whispers of your soul; listen to them.": "Los sueños son susurros de tu alma; escúchalos.",
        "Love is the music of the heart; let it play.": "El amor es la música del corazón; déjala sonar.",
        "Every challenge is an opportunity for growth.": "Cada desafío es una oportunidad para crecer.",
        "Knowledge comes from learning, wisdom comes from living.": "El conocimiento viene de aprender; la sabiduría, de vivir.",
        "Success is not final, failure is not fatal: it is the courage to continue that counts.": "El éxito no es definitivo ni el fracaso fatal: lo que cuenta es el valor de continuar.",
        "Choose happiness, choose to smile, choose to shine.": "Elige la felicidad, elige sonreír, elige brillar.",
        "Let your light shine so bright that others can see their way out of the dark.": "Haz que tu luz brille tan fuerte que otros encuentren su camino fuera de la oscuridad.",
        "Life is a journey; embrace every twist and turn.": "La vida es un viaje; abraza cada giro y vuelta.",
        "True love stories never have endings.": "Las historias de amor verdaderas nunca terminan.",
        "Dreams are today's answers to tomorrow's questions.": "Los sueños son las respuestas de hoy a las preguntas de mañana.",
    },
    "French": {
        "We, in our youth, dare to pursue our dreams, even facing hardship, we still believe in ourselves.": "Dans notre jeunesse, nous osons poursuivre nos rêves; même face aux épreuves nous croyons en nous.",
        "Don't be afraid of failure, for every setback is a step towards success.": "N'aie pas peur de l'échec, car chaque revers est un pas vers la réussite.",
        "Having a brave heart, youth is our greatest asset.": "Avec un cœur courageux, la jeunesse est notre plus grand atout.",
        "Treasure friendships, for they are the most beautiful memories of youth.": "Chéris les amitiés, car elles sont les plus beaux souvenirs de la jeunesse.",
        "Friends are the family we choose for ourselves.": "Les amis sont la famille que nous choisissons.",
        "Dreams are the whispers of your soul; listen to them.": "Les rêves sont les murmures de ton âme; écoute-les.",
        "Love is the music of the heart; let it play.": "L'amour est la musique du cœur; laisse-la jouer.",
        "Every challenge is an opportunity for growth.": "Chaque défi est une occasion de grandir.",
        "Knowledge comes from learning, wisdom comes from living.": "La connaissance vient de l'apprentissage, la sagesse vient de la vie.",
        "Success is not final, failure is not fatal: it is the courage to continue that counts.": "Le succès n'est pas final, l'échec n'est pas fatal: c'est le courage de continuer qui compte.",
        "Choose happiness, choose to smile, choose to shine.": "Choisis le bonheur, choisis de sourire, choisis de rayonner.",
        "Let your light shine so bright that others can see their way out of the dark.": "Fais briller ta lumière si fort que les autres puissent trouver leur chemin hors de l'obscurité.",
        "Life is a journey; embrace every twist and turn.": "La vie est un voyage; embrasse chaque détour.",
        "True love stories never have endings.": "Les vraies histoires d'amour n'ont pas de fin.",
        "Dreams are today's answers to tomorrow's questions.": "Les rêves sont les réponses d'aujourd'hui aux questions de demain.",
    },
    "Chinese (Simplified)": {
        "We, in our youth, dare to pursue our dreams, even facing hardship, we still believe in ourselves.": "青春的我们敢于追逐梦想，即使面对困难也始终相信自己。",
        "Don't be afraid of failure, for every setback is a step towards success.": "不要害怕失败，每一次挫折都是迈向成功的一步。",
        "Having a brave heart, youth is our greatest asset.": "拥有一颗勇敢的心，青春就是我们最大的财富。",
        "Treasure friendships, for they are the most beautiful memories of youth.": "珍惜友谊，因为它们是青春最美的记忆。",
        "Friends are the family we choose for ourselves.": "朋友是我们自己选择的家人。",
        "Dreams are the whispers of your soul; listen to them.": "梦想是灵魂的低语，要用心倾听。",
        "Love is the music of the heart; let it play.": "爱是心灵的乐章，让它自由奏响。",
        "Every challenge is an opportunity for growth.": "每一次挑战都是成长的机会。",
        "Knowledge comes from learning, wisdom comes from living.": "知识源于学习，智慧来自生活。",
        "Success is not final, failure is not fatal: it is the courage to continue that counts.": "成功不是终点，失败也非末日，关键在于继续前行的勇气。",
        "Choose happiness, choose to smile, choose to shine.": "选择快乐，选择微笑，选择闪耀。",
        "Let your light shine so bright that others can see their way out of the dark.": "让你的光芒如此耀眼，使他人也能走出黑暗。",
        "Life is a journey; embrace every twist and turn.": "人生是一场旅程，要拥抱每一次转折。",
        "True love stories never have endings.": "真正的爱情故事没有结局。",
        "Dreams are today's answers to tomorrow's questions.": "梦想是今天对明日提问的答案。",
    }
}

mood_translations = {
    "Spanish": {
        "Life is short, enjoy every moment!": "¡La vida es corta, disfruta cada momento!",
        "Let's embrace happiness!": "¡Abracemos la felicidad!",
        "Happiness is most important!": "¡La felicidad es lo más importante!",
        "When you're sad, remember to give yourself some time.": "Cuando estés triste, recuerda darte tiempo.",
        "Don't let anxiety control you, take a deep breath, everything will be okay.": "No dejes que la ansiedad te controle, respira profundo, todo estará bien.",
        "Be passionate and go for it!": "¡Sé apasionado y ve por ello!",
        "A peaceful mind is the source of happiness.": "Una mente en paz es la fuente de la felicidad.",
    },
    "French": {
        "Life is short, enjoy every moment!": "La vie est courte, profite de chaque instant !",
        "Let's embrace happiness!": "Embrassons le bonheur !",
        "Happiness is most important!": "Le bonheur est le plus important !",
        "When you're sad, remember to give yourself some time.": "Quand tu es triste, n'oublie pas de te laisser du temps.",
        "Don't let anxiety control you, take a deep breath, everything will be okay.": "Ne laisse pas l'anxiété te contrôler, respire profondément, tout ira bien.",
        "Be passionate and go for it!": "Sois passionné et lance-toi !",
        "A peaceful mind is the source of happiness.": "Un esprit paisible est la source du bonheur.",
    },
    "Chinese (Simplified)": {
        "Life is short, enjoy every moment!": "人生苦短，享受每一刻！",
        "Let's embrace happiness!": "让我们拥抱幸福！",
        "Happiness is most important!": "幸福最重要！",
        "When you're sad, remember to give yourself some time.": "当你伤心时，记得给自己一些时间。",
        "Don't let anxiety control you, take a deep breath, everything will be okay.": "不要让焦虑控制你，深呼吸，一切都会好起来。",
        "Be passionate and go for it!": "保持热情，勇敢追梦！",
        "A peaceful mind is the source of happiness.": "平和的心是幸福的源泉。",
    }
}
MOOD_QUOTES = {
    "Happy": [
        "Life is short, enjoy every moment!",
        "Let's embrace happiness!",
        "Happiness is most important!",
        "Happiness is when what you think, what you say, and what you do are in harmony.",
        "The best way to cheer yourself up is to try to cheer somebody else up.",
        "Joy comes from a content heart.",
        "Happiness is a choice, choose to smile at life."
    ],
    "Sad": [
        "When you're sad, remember to give yourself some time.",
        "Sadness is part of life, learn to accept it.",
        "It's okay to be sad, give yourself time to heal.",
        "Every cloud has a silver lining.",
        "Tears are words the heart can't express.",
        "Sadness is temporary, hope is eternal.",
        "Face sadness calmly to see hope."
    ],
    "Anxious": [
        "Don't let anxiety control you, take a deep breath, everything will be okay.",
        "Anxiety is not scary, the key is to find solutions.",
        "Anxiety is temporary, but your strength is permanent.",
        "Focus on what you can control, let go of what you can't.",
        "When anxious, take deep breaths and relax.",
        "Staying calm is the best way to face anxiety."
    ],
    "Excited": [
        "Be passionate and go for it!",
        "Pursue your dreams with passion and make them a reality!",
        "Channel your excitement into positive action.",
        "Let your enthusiasm light up the world.",
        "Excitement is the source of motivation.",
        "Passion is the key to success."
    ],
    "Calm": [
        "A peaceful mind is the source of happiness.",
        "Learn to observe calmly and experience true peace.",
        "In the midst of chaos, there is also opportunity.",
        "Peace comes from within.",
        "Tranquility is inner strength.",
        "Serenity leads to distance, take life slowly."
    ]
}
moods = list(MOOD_QUOTES.keys())

engine = None
glass_frames = set()
quote_card = None
background_canvas = None
scrollable_window = None

THEME_BACKGROUND_VARIANTS = {
    "Modern Light": [
        ("#f8fafc", "#e0f2fe", "#fce7f3"),
        ("#ffffff", "#fef3c7", "#e0f2fe"),
        ("#f9fafb", "#ede9fe", "#dbeafe")
    ],
    "Modern Dark": [
        ("#020617", "#0f172a", "#1e293b"),
        ("#050a1a", "#111827", "#1f2937"),
        ("#0b1120", "#1e293b", "#312e81")
    ],
    "Pastel": [
        ("#fff5f5", "#ffe4e6", "#fde4cf"),
        ("#fdf4ff", "#ede9fe", "#e0f2fe"),
        ("#fef9ef", "#fde2e4", "#e2ece9")
    ]
}

_active_background_variant = {}

def _hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))

def _rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)

def _blend_colors(color_a, color_b, weight=0.5):
    weight = max(0.0, min(1.0, weight))
    a_r, a_g, a_b = _hex_to_rgb(color_a)
    b_r, b_g, b_b = _hex_to_rgb(color_b)
    blended = (
        int(a_r * (1 - weight) + b_r * weight),
        int(a_g * (1 - weight) + b_g * weight),
        int(a_b * (1 - weight) + b_b * weight)
    )
    return _rgb_to_hex(blended)



VOICE_BACKEND = None
VOICE_INIT_ERROR = None
VOICE_SUPPORTED = False

def _update_voice_toggle_state():
    toggle = globals().get("voice_toggle")
    voice_var = globals().get("voice_enabled")
    if toggle is None:
        return
    if not VOICE_SUPPORTED:
        if voice_var is not None:
            voice_var.set(False)
        try:
            toggle.state(["disabled"])
        except tk.TclError:
            pass
        label = "Voice unavailable"
        if sys.version_info[:2] >= (3, 13):
            label = "Voice (Python 3.13 unavailable)"
        toggle.configure(text=label)
        return
    try:
        toggle.state(["!disabled"])
    except tk.TclError:
        pass
    label = "Enable Voice"
    if VOICE_BACKEND == "powershell":
        label = "Voice (Windows speech)"
    toggle.configure(text=label)

def _switch_to_powershell_fallback(error=None):
    global VOICE_BACKEND, VOICE_SUPPORTED, VOICE_INIT_ERROR, engine
    if error:
        VOICE_INIT_ERROR = str(error)
    engine = None
    if platform.system() == "Windows":
        VOICE_BACKEND = "powershell"
        VOICE_SUPPORTED = True
        _update_voice_toggle_state()
        return True

    VOICE_BACKEND = None
    VOICE_SUPPORTED = False
    _update_voice_toggle_state()
    return False

def _initialize_voice_backend():
    global VOICE_BACKEND, VOICE_INIT_ERROR, VOICE_SUPPORTED, engine
    if VOICE_BACKEND is not None:
        return
    try:
        engine = pyttsx3.init()
        engine.getProperty("voices")
        VOICE_BACKEND = "pyttsx3"
        VOICE_SUPPORTED = True
    except Exception as exc:
        VOICE_INIT_ERROR = str(exc)
        if not _switch_to_powershell_fallback(exc):
            pass

_initialize_voice_backend()

VOICE_UNSUPPORTED_MESSAGE = "Voice playback is unavailable on this system."
if VOICE_INIT_ERROR and not VOICE_SUPPORTED:
    VOICE_UNSUPPORTED_MESSAGE += f"\nEngine error: {VOICE_INIT_ERROR}"

def ensure_voice_engine():
    if VOICE_BACKEND != "pyttsx3":
        return None
    global engine
    if engine is None:
        try:
            engine = pyttsx3.init()
            engine.getProperty("voices")
        except Exception as exc:
            if not _switch_to_powershell_fallback(exc):
                return None
            return None
    return engine

def _speak_with_powershell(text):
    encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
    ps_command = (
        f"$bytes = [Convert]::FromBase64String('{encoded}');"
        "$text = [System.Text.Encoding]::UTF8.GetString($bytes);"
        "Add-Type -AssemblyName System.Speech;"
        "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
        "$synth.Speak($text);"
    )
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    subprocess.Popen(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps_command],
        creationflags=creationflags
    )

def _normalise_voice_text(text):
    if not text:
        return ""
    collapsed = " ".join(text.split())
    cleaned_chars = []
    for ch in collapsed:
        code_point = ord(ch)
        if code_point == 0xFE0F:
            continue
        if 0x1F000 <= code_point <= 0x1FAFF:
            continue
        category = unicodedata.category(ch)
        if category.startswith("C") or category.startswith("S"):
            continue
        cleaned_chars.append(ch)
    normalised = "".join(cleaned_chars).strip()
    return normalised





def _on_voice_toggle():
    voice_var = globals().get('voice_enabled')
    if voice_var is None:
        return
    if not voice_var.get():
        return
    quote_var = globals().get('current_quote')
    if quote_var is None:
        return
    speak_quote_text(quote_var.get())

def speak_quote_text(text):
    global VOICE_INIT_ERROR
    if not VOICE_SUPPORTED:
        return
    if 'voice_enabled' not in globals() or voice_enabled is None:
        return
    if not voice_enabled.get():
        return
    if not text or text.startswith("Click generate"):
        return

    voice_text = _normalise_voice_text(text)
    if not voice_text:
        return

    backend = VOICE_BACKEND

    if backend == "pyttsx3":
        voice_engine = ensure_voice_engine()
        if voice_engine is not None:
            try:
                voice_engine.say(voice_text)
                voice_engine.runAndWait()
                return
            except Exception as exc:
                if _switch_to_powershell_fallback(exc):
                    backend = VOICE_BACKEND
                else:
                    voice_enabled.set(False)
                    _update_voice_toggle_state()
                    messagebox.showwarning(
                        "Voice unavailable",
                        "We couldn't play the voice for this quote. Voice has been temporarily disabled."
                    )
                    print(f"Voice playback failed: {exc}")
                    return
        else:
            if not _switch_to_powershell_fallback(VOICE_INIT_ERROR):
                voice_enabled.set(False)
                _update_voice_toggle_state()
                if VOICE_INIT_ERROR:
                    print(f"Voice playback failed: {VOICE_INIT_ERROR}")
                messagebox.showwarning(
                    "Voice unavailable",
                    "We couldn't play the voice for this quote. Voice has been temporarily disabled."
                )
                return
            backend = VOICE_BACKEND

    if backend == "powershell":
        try:
            _speak_with_powershell(voice_text)
            return
        except Exception as exc:
            VOICE_INIT_ERROR = str(exc)
            print(f"Voice playback failed: {exc}")

    voice_enabled.set(False)
    _update_voice_toggle_state()
    messagebox.showwarning(
        "Voice unavailable",
        "We couldn't play the voice for this quote. Voice has been temporarily disabled."
    )

def load_user_data():
    global users, user_quotes, quote_ratings, quote_comments
    global custom_quotes, achievements, favorite_quotes
    global language_preferences, reflection_entries, ai_settings, user_goals
    if os.path.exists("user_data.json"):
        with open("user_data.json", "r") as file:
            data = json.load(file)
            users = data.get("users", {})
            loaded_quotes = defaultdict(list, data.get("user_quotes", {}))
            # Normalise quote history so that legacy entries (plain strings) still work
            normalised_quotes = defaultdict(list)
            for user, quotes_list in loaded_quotes.items():
                for item in quotes_list:
                    if isinstance(item, dict):
                        normalised_quotes[user].append(item)
                    else:
                        normalised_quotes[user].append({
                            "quote": item,
                            "timestamp": None
                        })
            user_quotes = defaultdict(list, normalised_quotes)
            quote_ratings = defaultdict(list, data.get("quote_ratings", {}))
            quote_comments = defaultdict(list, data.get("quote_comments", {}))
            custom_quotes = data.get("custom_quotes", [])
            achievements = defaultdict(list, data.get("achievements", {}))
            favorite_quotes = defaultdict(
                list,
                {user: list(favs) for user, favs in data.get("favorite_quotes", {}).items()}
            )
            language_preferences = data.get("language_preferences", {})
            reflection_entries = defaultdict(
                list,
                {
                    user: list(entries)
                    for user, entries in data.get("reflection_entries", {}).items()
                }
            )
            user_goals = defaultdict(
                list,
                {
                    user: [dict(goal) for goal in goals]
                    for user, goals in data.get("user_goals", {}).items()
                }
            )
            stored_ai = data.get("ai_settings")
            if isinstance(stored_ai, dict):
                ai_settings = _merge_ai_settings(stored_ai)
            else:
                stored_openai = data.get("openai_settings", {})
                if isinstance(stored_openai, dict):
                    ai_settings = _merge_ai_settings({"openai": {"api_key": stored_openai.get("api_key")}})

def save_user_data():
    data = {
        "users": users,
        "user_quotes": dict(user_quotes),
        "quote_ratings": dict(quote_ratings),
        "quote_comments": dict(quote_comments),
        "custom_quotes": custom_quotes,
        "achievements": dict(achievements),
        "favorite_quotes": dict(favorite_quotes),
        "language_preferences": language_preferences,
        "reflection_entries": dict(reflection_entries),
        "user_goals": dict(user_goals),
        "ai_settings": ai_settings,
        "openai_settings": {"api_key": ai_settings.get("openai", {}).get("api_key", "")}
    }
    with open("user_data.json", "w") as file:
        json.dump(data, file)

root = tk.Tk()
root.title("Youthful Quote Generator")
root.geometry("820x720")
root.minsize(720, 680)
voice_enabled = tk.BooleanVar(value=VOICE_SUPPORTED)

background_canvas = tk.Canvas(root, highlightthickness=0, bd=0)
background_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
try:
    # Canvas.lower on a Canvas object maps to tag_lower and requires arguments
    # calling it without args raises a TclError. We only want to ensure the
    # background canvas is visually behind other widgets; if lowering by widget
    # isn't supported we silently ignore the operation.
    background_canvas.lower()
except tk.TclError:
    pass

mood_var = tk.StringVar(value=moods[0])
language_var = tk.StringVar(value=language_options[0])

themes = {
    "Modern Light": {
        "bg": "#FFFFFF",
        "fg": "#2C3E50",
        "button_bg": "#ECF0F1",
        "accent": "#3498DB",
        "hover": "#2980B9",
        "card_bg": "#F8F9FA",
        "border": "#E9ECEF"
    },
    "Modern Dark": {
        "bg": "#1A1A1A",
        "fg": "#FFFFFF",
        "button_bg": "#2D2D2D",
        "accent": "#6C5CE7",
        "hover": "#5B4BC5",
        "card_bg": "#2D2D2D",
        "border": "#3D3D3D"
    },
    "Pastel": {
        "bg": "#FFF5F5",
        "fg": "#2D3436",
        "button_bg": "#FFE8E8",
        "accent": "#FF9999",
        "hover": "#FF7777",
        "card_bg": "#FFFFFF",
        "border": "#FFD1D1"
    },
    "Liquid Glass": {
        "bg": "#0f172a",
        "fg": "#f8fafc",
        "button_bg": "#1e293b",
        "accent": "#38bdf8",
        "hover": "#0ea5e9",
        "card_bg": "#1b253f",
        "border": "#2dd4bf",
        "glow": "#38bdf8"
    }
}

AI_FOUNDATIONS = {
    "Courage": {
        "sparks": [
            "the brave pulse in your chest",
            "the fearless whisper that urges you onward",
            "your quiet courage waiting to rise"
        ],
        "actions": [
            "turns trembling steps into bold strides",
            "reframes every doubt as a daring experiment",
            "translates uncertainty into unstoppable motion"
        ],
        "challenges": [
            "the horizon blurs",
            "your path feels uncharted",
            "storms test your resolve"
        ],
        "rewards": [
            "a new chapter of strength unfolds",
            "tomorrow salutes your daring heart",
            "your story glows with fearless colour"
        ]
    },
    "Dreams": {
        "sparks": [
            "the blueprint swirling in your imagination",
            "the stardust idea you keep close",
            "your constellation of what-ifs"
        ],
        "actions": [
            "maps detours into discoveries",
            "weaves ambition into gentle rituals",
            "turns late-night sketches into sunrise realities"
        ],
        "challenges": [
            "the night feels quiet",
            "progress seems slow",
            "doubt taps on the window"
        ],
        "rewards": [
            "a dream steps closer, smiling",
            "possibility plants roots in your tomorrow",
            "the future sends you a grateful wink"
        ]
    },
    "Friendship": {
        "sparks": [
            "the laughter echoing between you",
            "the shared memories stitched into your day",
            "the hand that always finds yours"
        ],
        "actions": [
            "turns ordinary chats into courage",
            "reminds you that you never walk alone",
            "translates silence into understanding"
        ],
        "challenges": [
            "distance stretches",
            "schedules scatter",
            "the world feels a little loud"
        ],
        "rewards": [
            "connection makes the journey softer",
            "your circle glows with shared light",
            "belonging blooms in every hello"
        ]
    },
    "Love": {
        "sparks": [
            "the warmth resting in your palms",
            "the melody that hums when you think of them",
            "your heart's favourite sunrise"
        ],
        "actions": [
            "turns whispers into promises",
            "chooses patience over perfection",
            "paints ordinary moments with wonder"
        ],
        "challenges": [
            "questions flutter in your chest",
            "longing lingers in the air",
            "vulnerability feels like a cliff edge"
        ],
        "rewards": [
            "trust becomes your favourite song",
            "two stories weave a shared future",
            "every heartbeat learns a new harmony"
        ]
    },
    "Life": {
        "sparks": [
            "the rhythm of possibilities",
            "your curiosity stretching wide",
            "the gentle hum of becoming"
        ],
        "actions": [
            "turns routine into ritual",
            "collects tiny joys like treasures",
            "translates mistakes into playful lessons"
        ],
        "challenges": [
            "the pace quickens",
            "to-do lists tower",
            "balance feels like a dance"
        ],
        "rewards": [
            "your story gathers vibrant chapters",
            "gratitude sparkles in small corners",
            "each sunrise cheers for you"
        ]
    },
    "Growth": {
        "sparks": [
            "the questions you keep asking",
            "your willingness to be a beginner",
            "the resilience rooted in your spirit"
        ],
        "actions": [
            "turns lessons into lived wisdom",
            "lets patience bloom between milestones",
            "celebrates every inch forward"
        ],
        "challenges": [
            "progress hides in the shadows",
            "old comfort zones wave back",
            "change arrives with unexpected timing"
        ],
        "rewards": [
            "your perspective becomes a sunrise",
            "confidence grows quietly and steadily",
            "you recognise your evolving self"
        ]
    },
    "Wisdom": {
        "sparks": [
            "the questions tucked behind your smile",
            "the lessons you collect like seashells",
            "your curiosity about the why"
        ],
        "actions": [
            "listens before leaping",
            "translates experience into insight",
            "offers gentle lanterns for others"
        ],
        "challenges": [
            "answers arrive slowly",
            "contradictions share the stage",
            "patience is asked of you"
        ],
        "rewards": [
            "clarity pours like warm tea",
            "your voice becomes a trusted compass",
            "understanding wraps around your choices"
        ]
    },
    "Success": {
        "sparks": [
            "the ambition humming in your bones",
            "your relentless curiosity",
            "the goals sketched in your notebook"
        ],
        "actions": [
            "turns planning into playful experimentation",
            "transforms setbacks into design notes",
            "keeps rhythm with steady progress"
        ],
        "challenges": [
            "deadlines knock loudly",
            "metrics demand attention",
            "comparison clouds the view"
        ],
        "rewards": [
            "momentum high-fives your persistence",
            "your impact echoes beyond today",
            "celebrations wait at every milestone"
        ]
    },
    "Happiness": {
        "sparks": [
            "the laughter tucked in your pockets",
            "your talent for finding little joys",
            "sunbeams resting on your shoulders"
        ],
        "actions": [
            "turns tiny wins into confetti",
            "mixes kindness into every plan",
            "shares smiles like bright postcards"
        ],
        "challenges": [
            "clouds gather without warning",
            "energy dips in the afternoon",
            "the world feels a little grey"
        ],
        "rewards": [
            "gratitude dances in your steps",
            "joy multiplies when you pass it on",
            "your sparkle lights the room"
        ]
    },
    "Inspiration": {
        "sparks": [
            "the muse perched on your shoulder",
            "ideas fluttering like paper cranes",
            "the spark that ignites your imagination"
        ],
        "actions": [
            "turns blank pages into playgrounds",
            "collects fragments and weaves them into magic",
            "lets curiosity lead the choreography"
        ],
        "challenges": [
            "motivation naps for a moment",
            "silence fills the studio",
            "your inner critic clears its throat"
        ],
        "rewards": [
            "fresh ideas bloom in technicolour",
            "your creativity invites others to dream",
            "the project ahead starts humming"
        ]
    }
}

AI_MOOD_INFUSIONS = {
    "Happy": {
        "tones": [
            "Today, joy stands beside you,",
            "With a bright grin, the universe whispers,",
            "Sunlight applauds you softly,"
        ],
        "nudges": [
            "Share that sparkle with someone close.",
            "Celebrate the tiny victories and let them grow.",
            "Let your laughter be the soundtrack of the day."
        ]
    },
    "Sad": {
        "tones": [
            "Even in gentle tears, a soft hope says,",
            "A quiet comfort sits with you and hums,",
            "Through the hush of today, a caring voice notes,"
        ],
        "nudges": [
            "Hold yourself kindly; healing is already on the way.",
            "Let someone you trust borrow the weight for a moment.",
            "Rest is courageous — breathe until the colours return."
        ]
    },
    "Anxious": {
        "tones": [
            "Slow breaths steady the room as a reminder whispers,",
            "Amid the hum of thoughts, a calm anchor tells you,",
            "With each inhale, a reassuring note declares,"
        ],
        "nudges": [
            "Take one grounded step; the rest will greet you later.",
            "Name three things you trust right now.",
            "Let today unfold at the pace of kindness."
        ]
    },
    "Excited": {
        "tones": [
            "Your enthusiasm drums like a festival,",
            "Energy fireworks pop around you,",
            "Momentum high-fives you loudly,"
        ],
        "nudges": [
            "Channel it into one bold move today.",
            "Invite someone to join the celebration.",
            "Take notes — future you will love this spark."
        ]
    },
    "Calm": {
        "tones": [
            "Peace pours over you like warm tea,",
            "Serenity nestles beside you,",
            "A gentle breeze affirms,"
        ],
        "nudges": [
            "Stay present; you're exactly where you need to be.",
            "Let this softness refill your energy.",
            "Carry this stillness into your next brave step."
        ]
    }
}

AI_STRUCTURES = [
    "{tone} {spark} {action}; even when {challenge}, {reward} {nudge}",
    "When {challenge}, remember {spark} {action}. {tone} {nudge}",
    "{tone} because {spark} {action}; {reward}. {nudge}"
]


def build_local_ai_quote(theme, mood):
    theme_data = AI_FOUNDATIONS.get(theme, AI_FOUNDATIONS["Inspiration"])
    mood_data = AI_MOOD_INFUSIONS.get(mood, AI_MOOD_INFUSIONS["Calm"])
    structure = random.choice(AI_STRUCTURES)
    return structure.format(
        tone=random.choice(mood_data["tones"]),
        spark=random.choice(theme_data["sparks"]),
        action=random.choice(theme_data["actions"]),
        challenge=random.choice(theme_data["challenges"]),
        reward=random.choice(theme_data["rewards"]),
        nudge=random.choice(mood_data["nudges"])
    )


def get_active_ai_provider():
    return _normalise_ai_provider(ai_settings.get("provider"))


def get_ai_provider_settings(provider=None):
    provider = _normalise_ai_provider(provider or get_active_ai_provider())
    return provider, ai_settings.get(provider, {})


def is_ai_provider_configured(provider=None):
    provider, settings = get_ai_provider_settings(provider)
    key = (settings.get("api_key") or "").strip()
    return bool(key), provider, settings


def _call_openai_chat(settings, system_prompt, user_prompt, temperature=0.8, max_tokens=160):
    api_key = (settings.get("api_key") or "").strip()
    if not api_key:
        return None, "OpenAI API key is not configured. Add it from AI Settings to unlock live quotes."

    payload = {
        "model": settings.get("model") or OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "n": 1,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    endpoint = settings.get("endpoint") or OPENAI_API_URL
    timeout = settings.get("timeout") or OPENAI_TIMEOUT

    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            return None, "AI service returned no quote."
        content = choices[0].get("message", {}).get("content")
        if not content:
            return None, "AI service returned empty content."
        return content.strip(), None
    except requests.exceptions.RequestException as exc:
        return None, f"Failed to contact AI service: {exc}"
    except (ValueError, KeyError, TypeError) as exc:
        return None, f"Unexpected AI response: {exc}"


def _call_openrouter_chat(settings, system_prompt, user_prompt, temperature=0.8, max_tokens=160):
    api_key = (settings.get("api_key") or "").strip()
    if not api_key:
        return None, "OpenRouter API key is not configured. Add it from AI Settings to unlock live quotes."

    payload = {
        "model": settings.get("model") or OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "n": 1,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    app_url = settings.get("app_url") or os.getenv("OPENROUTER_APP_URL")
    app_name = settings.get("app_name") or os.getenv("OPENROUTER_APP_NAME")
    if app_url:
        headers["HTTP-Referer"] = app_url
    if app_name:
        headers["X-Title"] = app_name

    endpoint = settings.get("endpoint") or OPENROUTER_API_URL
    timeout = settings.get("timeout") or OPENROUTER_TIMEOUT

    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            return None, "AI service returned no quote."
        content = choices[0].get("message", {}).get("content")
        if not content:
            return None, "AI service returned empty content."
        return content.strip(), None
    except requests.exceptions.RequestException as exc:
        return None, f"Failed to contact AI service: {exc}"
    except (ValueError, KeyError, TypeError) as exc:
        return None, f"Unexpected AI response: {exc}"


def _call_gemini_chat(settings, system_prompt, user_prompt, temperature=0.8, max_tokens=160):
    api_key = (settings.get("api_key") or "").strip()
    if not api_key:
        return None, "Gemini API key is not configured. Add it from AI Settings to unlock live quotes."

    combined_prompt = f"{system_prompt}\n\n{user_prompt}".strip()
    payload = {
        "contents": [
            {"parts": [{"text": combined_prompt}]}
        ],
        "generationConfig": {
            "temperature": float(temperature),
            "maxOutputTokens": max_tokens,
        },
    }

    endpoint = (settings.get("endpoint") or GEMINI_API_URL).rstrip("/")
    model = settings.get("model") or GEMINI_MODEL
    timeout = settings.get("timeout") or GEMINI_TIMEOUT
    url = f"{endpoint}/models/{model}:generateContent?key={api_key}"

    try:
        response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        candidates = data.get("candidates") or []
        for candidate in candidates:
            parts = candidate.get("content", {}).get("parts", [])
            texts = [part.get("text", "").strip() for part in parts if part.get("text")]
            if texts:
                combined = " ".join(texts).strip()
                if combined:
                    return combined, None
        prompt_feedback = data.get("promptFeedback", {})
        if prompt_feedback.get("blockReason"):
            return None, f"Gemini blocked the prompt: {prompt_feedback['blockReason']}"
        return None, "AI service returned empty content."
    except requests.exceptions.RequestException as exc:
        return None, f"Failed to contact AI service: {exc}"
    except (ValueError, KeyError, TypeError) as exc:
        return None, f"Unexpected AI response: {exc}"


def call_ai_chat(system_prompt, user_prompt, temperature=0.8, max_tokens=160):
    provider = get_active_ai_provider()
    _, settings = get_ai_provider_settings(provider)
    if provider == "openrouter":
        return _call_openrouter_chat(settings, system_prompt, user_prompt, temperature, max_tokens)
    if provider == "gemini":
        return _call_gemini_chat(settings, system_prompt, user_prompt, temperature, max_tokens)
    return _call_openai_chat(settings, system_prompt, user_prompt, temperature, max_tokens)


def request_live_quote(theme, mood, language):
    system_prompt = (
        "You craft short, uplifting quotes for young dreamers. "
        "Return a single quote under two sentences without extra commentary."
    )
    user_prompt = (
        f"Theme: {theme}. Mood: {mood}. "
        f"Write one inspirational quote tailored for teenagers. "
        f"Deliver it in {language}."
    )
    return call_ai_chat(system_prompt, user_prompt, temperature=0.8, max_tokens=120)


def request_ai_translation(text, language):
    system_prompt = (
        "You are a precise translation assistant. Translate quotes faithfully while preserving tone. "
        "Return only the translated quote without additional commentary."
    )
    user_prompt = f"Translate this quote into {language}: {text}"
    return call_ai_chat(system_prompt, user_prompt, temperature=0.2, max_tokens=180)



style = ttk.Style()
try:
    if "clam" in style.theme_names():
        style.theme_use("clam")
except tk.TclError:
    pass
current_theme = tk.StringVar(value="Modern Light")

def get_theme_colors():
    return themes.get(current_theme.get(), themes["Modern Light"])

def get_selected_language():
    selected = language_var.get()
    if selected not in language_options:
        return "English"
    return selected

def ensure_dynamic_translation(cache, text, language):
    translation = cache.get(language, {}).get(text) if cache else None
    if translation:
        return translation, None
    configured, provider, _settings = is_ai_provider_configured()
    if not configured:
        provider_name = provider.capitalize() if provider else "AI"
        return None, f"Configure {provider_name} in AI Settings to translate into {language}."
    translated, error = request_ai_translation(text, language)
    if translated:
        cleaned = translated.strip()
        cleaned = cleaned.strip('"').strip('“”')
        cache.setdefault(language, {})[text] = cleaned
        return cleaned, None
    return None, error


def translate_quote_text(text):
    language = get_selected_language()
    if language == "English" or not text:
        return text
    translation = quote_translations.get(language, {}).get(text)
    if translation:
        return f"{translation}\n\n({text})"
    translated, error = ensure_dynamic_translation(quote_translations, text, language)
    if translated:
        return f"{translated}\n\n({text})"
    if error:
        cleaned_error = error.replace("\n", " ").strip()
        return f"{text}\n\n([{language} translation unavailable — {cleaned_error}])"
    return text

def translate_mood_text(text):
    language = get_selected_language()
    if language == "English" or not text:
        return text
    translation = mood_translations.get(language, {}).get(text)
    if translation:
        return f"{translation}\n\n({text})"
    translated, error = ensure_dynamic_translation(mood_translations, text, language)
    if translated:
        return f"{translated}\n\n({text})"
    if error:
        cleaned_error = error.replace("\n", " ").strip()
        return f"{text}\n\n([{language} translation unavailable — {cleaned_error}])"
    return text

def localise_any_quote(text):
    if not text:
        return text
    for mood_list in MOOD_QUOTES.values():
        if text in mood_list:
            return translate_mood_text(text)
    return translate_quote_text(text)

current_quote_kind = "theme"

def record_quote_history(username, quote):
    entry = {
        "quote": quote,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "language": get_selected_language()
    }
    user_quotes[username].append(entry)
    save_user_data()
    update_achievements(username)

def update_achievements(username):
    unlocked = set(achievements[username])
    history_count = len(user_quotes[username])
    new_achievements = []

    if history_count >= 1 and "First Quote" not in unlocked:
        new_achievements.append("First Quote: Generated your first dose of inspiration!")
    if history_count >= 10 and "Quote Explorer" not in unlocked:
        new_achievements.append("Quote Explorer: Generated 10 quotes.")

    favourite_count = len(favorite_quotes[username])
    if favourite_count >= 3 and "Heart Collector" not in unlocked:
        new_achievements.append("Heart Collector: Saved 3 favourite quotes.")

    ratings_given = sum(
        1 for ratings in quote_ratings.values() for user, _ in ratings if user == username
    )
    if ratings_given >= 5 and "Helpful Critic" not in unlocked:
        new_achievements.append("Helpful Critic: Rated 5 quotes.")

    reflections_logged = len(reflection_entries[username])
    if reflections_logged >= 3 and "Reflection Keeper" not in unlocked:
        new_achievements.append("Reflection Keeper: Logged 3 reflections.")

    goals_created = len(user_goals[username])
    if goals_created >= 1 and "Vision Setter" not in unlocked:
        new_achievements.append("Vision Setter: Planned your first personal goal.")

    goals_completed = sum(1 for goal in user_goals[username] if goal.get("completed"))
    if goals_completed >= 1 and "Momentum Master" not in unlocked:
        new_achievements.append("Momentum Master: Completed a personal goal.")
    if goals_completed >= 5 and "Trailblazer" not in unlocked:
        new_achievements.append("Trailblazer: Completed five personal goals.")

    preferred_language = language_preferences.get(username)
    if preferred_language and preferred_language != "English" and "Polyglot Dreamer" not in unlocked:
        new_achievements.append("Polyglot Dreamer: Enjoyed quotes in another language.")

    if new_achievements:
        achievements[username].extend(new_achievements)
        save_user_data()
        messagebox.showinfo(
            "Achievements unlocked!",
            "\n".join(new_achievements)
        )

def calculate_average_rating(quote):
    ratings = quote_ratings.get(quote, [])
    if not ratings:
        return None
    return sum(score for _, score in ratings) / len(ratings)

def format_history_entry(entry):
    quote = entry.get("quote", "")
    timestamp = entry.get("timestamp")
    display = localise_any_quote(quote)
    language_used = entry.get("language")
    if timestamp:
        label = f"[{timestamp}] {display}"
    else:
        label = display
    if language_used and language_used != get_selected_language():
        label += f"\n🌐 Saved in {language_used}"
    return label

def format_reflection_entry(entry):
    timestamp = entry.get("timestamp")
    mood = entry.get("mood", "")
    gratitude = entry.get("gratitude")
    insight = entry.get("insight")
    intention = entry.get("intention")
    language_used = entry.get("language")

    lines = []
    if timestamp:
        lines.append(f"[{timestamp}] {mood or 'Reflection'}")
    elif mood:
        lines.append(mood)
    if gratitude:
        lines.append(f"Grateful for: {gratitude}")
    if insight:
        lines.append(f"Insight: {insight}")
    if intention:
        lines.append(f"Next step: {intention}")
    if language_used and language_used != get_selected_language():
        lines.append(f"🌐 Captured in {language_used}")
    return "\n".join(lines)



EMOJIS = {
    "generate": "\u2728",
    "share": "\U0001f4e4",
    "rate": "\u2b50",
    "register": "\U0001f195",
    "login": "\U0001f511",
    "profile": "\U0001f464",
    "mood": "\U0001f308",
    "voice": "\U0001f399",
    "search": "\U0001f50d",
    "comment": "\U0001f4ac",
    "custom": "\u270f",
    "recommend": "\U0001f3af",
    "exit": "\U0001f6aa",
    "copy": "\U0001f4cb",
    "favorite": "\u2764",
    "insights": "\U0001f4ca",
    "ai": "\U0001f916",
    "journal": "\U0001f4dd",
    "story": "\U0001f4da",
    "goals": "\U0001f4c8",
    "language": "\U0001f30d",
    "api_settings": "\u2699",
    "export": "\U0001f4e6",
    "github": "\U0001f431"
}

def configure_button_style():
    theme_colors = get_theme_colors()
    style.configure(
        "Custom.TButton",
        padding=(20, 12),
        relief="flat",
        background=theme_colors["button_bg"],
        foreground=theme_colors["fg"],
        font=("Segoe UI", 11),
        borderwidth=0,
        focuscolor=theme_colors["accent"]
    )

    style.map("Custom.TButton",
        background=[("active", theme_colors["hover"])],
        foreground=[("active", "#FFFFFF")]
    )

    style.configure("TFrame", background=theme_colors["bg"])
    style.configure("TLabel", background=theme_colors["bg"], foreground=theme_colors["fg"])

    style.configure(
        "Card.TFrame",
        background=theme_colors["card_bg"],
        relief="solid",
        borderwidth=1,
        bordercolor=theme_colors["border"]
    )

    style.configure(
        "TCombobox",
        background=theme_colors["button_bg"],
        fieldbackground=theme_colors["bg"],
        foreground=theme_colors["fg"],
        arrowcolor=theme_colors["accent"]
    )

    style.configure(
        "Custom.TCheckbutton",
        background=theme_colors["card_bg"],
        foreground=theme_colors["fg"],
        font=("Segoe UI", 11)
    )

    style.map(
        "Custom.TCheckbutton",
        background=[("active", theme_colors["hover"])]
    )

    style.configure(
        "Info.TLabel",
        background=theme_colors["card_bg"],
        foreground=theme_colors["fg"],
        font=("Segoe UI", 10)
    )

    style.configure(
        "Link.TLabel",
        background=theme_colors["card_bg"],
        foreground=theme_colors["accent"],
        font=("Segoe UI", 10, "underline")
    )

    style.map(
        "Link.TLabel",
        foreground=[("active", theme_colors["hover"])]
    )

    root.configure(bg=get_theme_colors()["bg"])
    root.option_add('*TCombobox*Listbox.background', get_theme_colors()["bg"])
    root.option_add('*TCombobox*Listbox.foreground', get_theme_colors()["fg"])


def draw_liquid_glass_background(pulse=False):
    if background_canvas is None:
        return

    theme_name = current_theme.get()
    colors = get_theme_colors()
    background_canvas.delete("gradient")

    width = max(background_canvas.winfo_width(), 1)
    height = max(background_canvas.winfo_height(), 1)

    if theme_name != "Liquid Glass":
        variants = THEME_BACKGROUND_VARIANTS.get(theme_name)
        selected = _active_background_variant.get(theme_name)

        if variants:
            if pulse or selected is None:
                choices = [variant for variant in variants if variant != selected]
                selected = random.choice(choices or variants)
                _active_background_variant[theme_name] = selected

            base_color, accent_one, accent_two = selected
            background_canvas.configure(bg=base_color)

            background_canvas.create_rectangle(
                0,
                0,
                width,
                height,
                fill=base_color,
                outline="",
                tags="gradient"
            )

            background_canvas.create_oval(
                -0.45 * width,
                -0.2 * height,
                0.75 * width,
                0.8 * height,
                fill=accent_one,
                outline="",
                tags="gradient"
            )

            background_canvas.create_oval(
                0.2 * width,
                0.3 * height,
                1.1 * width,
                height + 0.6 * height,
                fill=accent_two,
                outline="",
                tags="gradient"
            )

            accent_overlay = _blend_colors(base_color, colors.get("accent", base_color), 0.35)
            background_canvas.create_oval(
                0.55 * width,
                -0.1 * height,
                width + 0.6 * width,
                0.7 * height,
                fill=accent_overlay,
                outline="",
                tags="gradient"
            )
        else:
            background_canvas.configure(bg=colors["bg"])

        try:
            background_canvas.lower("gradient")
        except tk.TclError:
            pass

        try:
            background_canvas.lower()
        except tk.TclError:
            pass
        return

    background_canvas.configure(bg=colors["bg"])

    glow_color = colors.get("glow", colors["accent"]) if "accent" in colors else colors.get("bg")
    highlight = colors.get("card_bg", colors["bg"])

    jitter_x = random.uniform(-0.08, 0.08) if pulse else 0
    jitter_y = random.uniform(-0.08, 0.08) if pulse else 0

    background_canvas.create_rectangle(
        0,
        0,
        width,
        height,
        fill=colors["bg"],
        outline="",
        tags="gradient"
    )

    background_canvas.create_oval(
        (-0.4 + jitter_x) * width,
        (-0.2 + jitter_y) * height,
        (0.8 + jitter_x) * width,
        height,
        fill=highlight,
        outline="",
        tags="gradient"
    )
    background_canvas.create_oval(
        (0.2 + jitter_x) * width,
        (0.1 + jitter_y) * height,
        (1.2 + jitter_x) * width,
        height + 0.4 * height,
        fill=glow_color,
        outline="",
        tags="gradient"
    )
    background_canvas.create_oval(
        (-0.2 + jitter_x) * width,
        (0.6 + jitter_y) * height,
        (0.6 + jitter_x) * width,
        height + 0.9 * height,
        fill=highlight,
        outline="",
        tags="gradient"
    )

    try:
        background_canvas.lower("gradient")
    except tk.TclError:
        pass

    try:
        background_canvas.lower()
    except tk.TclError:
        pass


def change_theme():
    theme = current_theme.get()
    theme_colors = themes[theme]
    root.config(bg=theme_colors["bg"])
    configure_button_style()

    for widget in root.winfo_children():
        update_widget_colors(widget, theme_colors)
    draw_liquid_glass_background(pulse=True)
    update_quote_wrap_width()

def update_widget_colors(widget, colors):
    if widget is background_canvas:
        widget.configure(bg=colors["bg"])
    elif widget in glass_frames:
        widget.configure(
            bg=colors["card_bg"],
            highlightbackground=colors["border"],
            highlightcolor=colors["border"],
            highlightthickness=1
        )
    if widget is quote_label:
        widget.configure(bg=colors["card_bg"], fg=colors["fg"])
    elif isinstance(widget, tk.Label):
        widget.configure(bg=colors["bg"], fg=colors["fg"])
    elif isinstance(widget, tk.Frame) and widget not in glass_frames:
        widget.configure(bg=colors["bg"])
    elif isinstance(widget, tk.Menubutton):
        widget.configure(bg=colors["button_bg"], fg=colors["fg"])
    elif isinstance(widget, tk.Canvas):
        widget.configure(bg=colors["bg"])
    elif isinstance(widget, scrolledtext.ScrolledText):
        widget.configure(bg=colors["button_bg"], fg=colors["fg"])

    for child in widget.winfo_children():
        update_widget_colors(child, colors)

def configure_voice():
    if not VOICE_SUPPORTED:
        messagebox.showinfo("Voice unavailable", VOICE_UNSUPPORTED_MESSAGE)
        return
    if VOICE_BACKEND != "pyttsx3":
        messagebox.showinfo(
            "Voice settings",
            "Voice settings are available only when the pyttsx3 voice engine is active."
        )
        return

    voice_engine = ensure_voice_engine()
    if voice_engine is None:
        messagebox.showwarning(
            "Voice unavailable",
            "We couldn't load the voice engine. Try again after restarting the app."
        )
        return

    voice_window = tk.Toplevel(root)
    voice_window.title("Voice Settings")
    voice_window.geometry("300x200")
    update_widget_colors(voice_window, get_theme_colors())

    speed_scale = ttk.Scale(voice_window, from_=0, to=200, orient="horizontal")
    speed_scale.set(voice_engine.getProperty('rate'))
    speed_scale.pack(pady=10)

    volume_scale = ttk.Scale(voice_window, from_=0, to=1, orient="horizontal")
    volume_scale.set(voice_engine.getProperty('volume'))
    volume_scale.pack(pady=10)

    def apply_settings():
        current_engine = ensure_voice_engine()
        if current_engine is None:
            messagebox.showwarning(
                "Voice unavailable",
                "We couldn't load the voice engine. Please try again later."
            )
            return
        current_engine.setProperty('rate', speed_scale.get())
        current_engine.setProperty('volume', volume_scale.get())
        voice_window.destroy()

    ttk.Button(voice_window, text="Apply", command=apply_settings).pack(pady=10)


def configure_openai():
    settings_window = tk.Toplevel(root)
    settings_window.title("AI Settings")
    settings_window.geometry("420x360")

    provider_labels = {provider: AI_PROVIDER_NAMES[provider] for provider in SUPPORTED_AI_PROVIDERS}
    label_to_provider = {label: key for key, label in provider_labels.items()}
    info_copy = {
        "openai": (
            "Connect with OpenAI to stream fresh quotes. Your API key stays on this device "
            "inside user_data.json."
        ),
        "openrouter": (
            "Use OpenRouter to access a community hub of models, including OpenAI-compatible ones. "
            "Set your API key (and optional app URL/name for rate limits)."
        ),
        "gemini": (
            "Tap into Google Gemini for creative quotes. Provide your Gemini API key to begin."
        ),
    }
    env_vars = {
        "openai": "OPENAI_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
        "gemini": "GEMINI_API_KEY",
    }

    def default_model(provider):
        if provider == "openrouter":
            return OPENROUTER_MODEL
        if provider == "gemini":
            return GEMINI_MODEL
        return OPENAI_MODEL

    active_provider_var = tk.StringVar(value=get_active_ai_provider())
    provider_display_var = tk.StringVar(value=provider_labels[active_provider_var.get()])

    info_label = tk.Label(settings_window, wraplength=360, justify="left")
    info_label.pack(padx=20, pady=(20, 12), anchor="w")

    provider_frame = tk.Frame(settings_window)
    provider_frame.pack(fill=tk.X, padx=20, pady=(0, 12))

    tk.Label(provider_frame, text="Provider:").grid(row=0, column=0, sticky="w")
    provider_select = ttk.Combobox(
        provider_frame,
        textvariable=provider_display_var,
        values=[provider_labels[p] for p in SUPPORTED_AI_PROVIDERS],
        state="readonly"
    )
    provider_select.grid(row=0, column=1, sticky="ew", padx=(8, 0))
    provider_frame.columnconfigure(1, weight=1)

    entry_frame = tk.Frame(settings_window)
    entry_frame.pack(fill=tk.X, padx=20)

    key_label_var = tk.StringVar()
    tk.Label(entry_frame, textvariable=key_label_var).pack(anchor="w")

    key_var = tk.StringVar()
    model_var = tk.StringVar()
    app_url_var = tk.StringVar()
    app_name_var = tk.StringVar()
    show_key = tk.BooleanVar(value=False)

    key_entry = ttk.Entry(entry_frame, textvariable=key_var, show="•")
    key_entry.pack(fill=tk.X, pady=(4, 0))

    def toggle_visibility():
        key_entry.configure(show="" if show_key.get() else "•")

    ttk.Checkbutton(
        entry_frame,
        text="Show key",
        variable=show_key,
        command=toggle_visibility,
        style="Custom.TCheckbutton"
    ).pack(anchor="w", pady=(6, 0))

    model_label = tk.Label(entry_frame, text="Model ID:")
    model_label.pack(anchor="w", pady=(10, 0))
    ttk.Entry(entry_frame, textvariable=model_var).pack(fill=tk.X, pady=(4, 0))

    openrouter_frame = tk.Frame(settings_window)
    tk.Label(openrouter_frame, text="App URL (optional):").pack(anchor="w")
    ttk.Entry(openrouter_frame, textvariable=app_url_var).pack(fill=tk.X, pady=(4, 6))
    tk.Label(openrouter_frame, text="App Name (optional):").pack(anchor="w")
    ttk.Entry(openrouter_frame, textvariable=app_name_var).pack(fill=tk.X)

    status_var = tk.StringVar(value="")

    def refresh_fields(*_args):
        provider = _normalise_ai_provider(label_to_provider.get(provider_display_var.get()))
        active_provider_var.set(provider)
        provider_display_var.set(provider_labels[provider])
        info_label.configure(text=info_copy[provider])
        provider_settings = ai_settings.get(provider, {})
        key_label_var.set(f"{provider_labels[provider]} API Key:")
        key_var.set(provider_settings.get("api_key", ""))
        model_var.set(provider_settings.get("model", default_model(provider)))
        if provider == "openrouter":
            app_url_var.set(provider_settings.get("app_url", ""))
            app_name_var.set(provider_settings.get("app_name", ""))
            if not openrouter_frame.winfo_ismapped():
                openrouter_frame.pack(fill=tk.X, padx=20, pady=(12, 0))
        else:
            app_url_var.set(provider_settings.get("app_url", ""))
            app_name_var.set(provider_settings.get("app_name", ""))
            openrouter_frame.pack_forget()
        status_var.set("")

    provider_select.bind("<<ComboboxSelected>>", refresh_fields)

    def use_env_key():
        provider = active_provider_var.get()
        env_name = env_vars[provider]
        env_value = (os.getenv(env_name) or "").strip()
        if env_value:
            key_var.set(env_value)
            status_var.set(f"Loaded key from {env_name}.")
        else:
            status_var.set(f"No {env_name} environment variable detected.")
        if provider == "openrouter":
            env_app_url = (os.getenv("OPENROUTER_APP_URL") or "").strip()
            env_app_name = (os.getenv("OPENROUTER_APP_NAME") or "").strip()
            if env_app_url:
                app_url_var.set(env_app_url)
            if env_app_name:
                app_name_var.set(env_app_name)

    def save_settings():
        provider = active_provider_var.get()
        provider_settings = ai_settings.setdefault(provider, {})
        provider_settings["api_key"] = key_var.get().strip()
        provider_settings["model"] = model_var.get().strip() or default_model(provider)
        if provider == "openrouter":
            provider_settings["app_url"] = app_url_var.get().strip()
            provider_settings["app_name"] = app_name_var.get().strip()
        ai_settings["provider"] = provider
        # update environment helpers to smooth future loads
        if provider_settings["api_key"]:
            os.environ[env_vars[provider]] = provider_settings["api_key"]
        status_var.set("Settings saved for {}.".format(provider_labels[provider]))
        save_user_data()

    button_frame = tk.Frame(settings_window)
    button_frame.pack(fill=tk.X, padx=20, pady=(16, 0))

    ttk.Button(
        button_frame,
        text="Load from environment",
        command=use_env_key,
        style="Custom.TButton"
    ).pack(side=tk.LEFT)
    ttk.Button(
        button_frame,
        text="Save",
        command=save_settings,
        style="Custom.TButton"
    ).pack(side=tk.RIGHT)

    status_label = tk.Label(settings_window, textvariable=status_var, wraplength=360, justify="left")
    status_label.pack(padx=20, pady=(12, 16), anchor="w")

    refresh_fields()
    toggle_visibility()
    update_widget_colors(settings_window, get_theme_colors())

def search_quotes():
    search_term = simpledialog.askstring("Search", "Enter search term:")
    if search_term:
        results = []
        for category, quote_list in quotes.items():
            for quote in quote_list:
                if search_term.lower() in quote.lower():
                    results.append(quote)
        
        if results:
            result_window = tk.Toplevel(root)
            result_window.title("Search Results")
            result_text = scrolledtext.ScrolledText(result_window, width=50, height=10)
            result_text.pack(padx=10, pady=10)
            update_widget_colors(result_window, get_theme_colors())
            for quote in results:
                result_text.insert(tk.END, f"{quote}\n\n")
            result_text.config(state='disabled')
        else:
            messagebox.showinfo("Search", "No matching quotes found.")

main_frame = ttk.Frame(root, padding="24")
main_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(main_frame, highlightthickness=0, bd=0)
scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg=get_theme_colors()["bg"])
scrollable_frame.configure(padx=20, pady=20)

canvas.configure(yscrollcommand=scrollbar.set)
scrollable_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

quote_type_var = tk.StringVar(value="Courage")
quote_type_menu = tk.OptionMenu(scrollable_frame, quote_type_var, *quotes.keys())
quote_type_menu.config(font=("Arial", 12))
quote_type_menu.pack(pady=10)

def register():
    username = simpledialog.askstring("Register", "Please enter your username:")
    if username:
        if username not in users:
            users[username] = True
            language_preferences[username] = get_selected_language()
            save_user_data()
            messagebox.showinfo("Success", "Registration successful! Please log in.")
        else:
            messagebox.showerror("Error", "Username already exists!")

def login():
    username = simpledialog.askstring("Log In", "Please enter your username:")
    if username:
        if username in users:
            current_user.set(username)
            preferred_language = language_preferences.get(username)
            if preferred_language in language_options:
                language_var.set(preferred_language)
            else:
                language_var.set(language_options[0])
            messagebox.showinfo("Success", f"Log in successful, welcome {username}!")
        else:
            messagebox.showerror("Error", "Username does not exist!")

def logout():
    current_user.set("Not logged in")
    messagebox.showinfo("Success", "Logged out successfully!")

current_user = tk.StringVar(value="Not logged in")
current_original_quote = tk.StringVar(value="")
current_quote_prefix = tk.StringVar(value="")

def get_active_quote_base():
    base = current_original_quote.get()
    if base:
        return base
    displayed = current_quote.get()
    prefix = current_quote_prefix.get()
    if prefix and displayed.startswith(prefix):
        return displayed[len(prefix):].strip()
    return displayed

def refresh_current_quote_display():
    global current_quote_kind
    base = current_original_quote.get()
    if not base:
        return

    if current_quote_kind == "mood":
        translated = translate_mood_text(base)
    else:
        translated = translate_quote_text(base)

    prefix = current_quote_prefix.get()
    if prefix:
        current_quote.set(f"{prefix}\n{translated}")
    else:
        current_quote.set(translated)
    update_quote_wrap_width()

def on_language_change(*_):
    if current_user.get() != "Not logged in":
        language_preferences[current_user.get()] = get_selected_language()
        save_user_data()
        update_achievements(current_user.get())
    refresh_current_quote_display()

def show_quote():
    global current_quote_kind
    loading_label.config(text="Loading...")
    root.update()

    quote_list = quotes[quote_type_var.get()] + custom_quotes
    if not quote_list:
        loading_label.config(text="")
        messagebox.showwarning("Warning", "No quotes available in this category yet!")
        return

    quote = random.choice(quote_list)

    current_original_quote.set(quote)
    current_quote_prefix.set("")
    current_quote_kind = "theme"
    refresh_current_quote_display()
    theme_colors = get_theme_colors()
    quote_label.config(bg=theme_colors["card_bg"], fg=theme_colors["fg"])
    draw_liquid_glass_background(pulse=True)

    speak_quote_text(current_quote.get())

    if current_user.get() != "Not logged in":
        record_quote_history(current_user.get(), quote)

    loading_label.config(text="")

def generate_ai_quote():
    global current_quote_kind
    theme = quote_type_var.get()
    mood = mood_var.get()
    language = get_selected_language()

    provider_label = AI_PROVIDER_NAMES.get(get_active_ai_provider(), "AI")
    quote, error = request_live_quote(theme, mood, language)
    if quote:
        prefix = f"AI Muse — {theme} ({provider_label})"
    else:
        quote = build_local_ai_quote(theme, mood)
        prefix = f"AI Muse — {theme} (offline)"
        if error:
            messagebox.showwarning(
                "AI service unavailable",
                f"{error}\nShowing an offline creative quote instead."
            )
            if "API key is not configured" in error or "Configure" in error:
                if messagebox.askyesno(
                    "Update AI settings",
                    "Would you like to configure your AI provider now?"
                ):
                    configure_openai()

    current_original_quote.set(quote)
    current_quote_prefix.set(prefix)
    current_quote_kind = "theme"
    refresh_current_quote_display()
    quote_label.config(bg=get_theme_colors()["card_bg"], fg=get_theme_colors()["fg"])
    draw_liquid_glass_background(pulse=True)

    speak_quote_text(current_quote.get())

    if current_user.get() != "Not logged in":
        record_quote_history(current_user.get(), quote)


def rate_quote():
    if current_user.get() == "Not logged in":
        messagebox.showerror("Error", "Please log in first!")
        return

    quote = get_active_quote_base()
    if quote and not quote.startswith("Click generate"):
        rating = simpledialog.askinteger("Rate", "Please rate this quote (1-5):", minvalue=1, maxvalue=5)
        if rating:
            quote_ratings[quote].append((current_user.get(), rating))
            save_user_data()
            update_achievements(current_user.get())
            average = calculate_average_rating(quote)
            if average is not None:
                messagebox.showinfo(
                    "Success",
                    f"Rating recorded! Current average: {average:.1f}/5"
                )
            else:
                messagebox.showinfo("Success", "Rating successful!")
    else:
        messagebox.showwarning("Warning", "Please generate a quote first!")

def comment_quote():
    if current_user.get() == "Not logged in":
        messagebox.showerror("Error", "Please log in first!")
        return

    quote = get_active_quote_base()
    if quote and not quote.startswith("Click generate"):
        comment = simpledialog.askstring("Comment", "Please comment on this quote:")
        if comment:
            quote_comments[quote].append((current_user.get(), comment))
            save_user_data()
            messagebox.showinfo("Success", "Comment successful!")
    else:
        messagebox.showwarning("Warning", "Please generate a quote first!")

def add_custom_quote():
    custom_quote = simpledialog.askstring("Add Quote", "Please enter your custom quote:")
    if custom_quote:
        custom_quotes.append(custom_quote)
        save_user_data()
        messagebox.showinfo("Success", "Custom quote added successfully!")

def recommend_quote():
    if current_user.get() == "Not logged in":
        messagebox.showerror("Error", "Please log in first!")
        return

    if quote_ratings:
        recommended_quote = random.choice(list(quote_ratings.keys()))
        current_original_quote.set(recommended_quote)
        current_quote_prefix.set("Recommended Quote:")
        current_quote_kind = "theme"
        refresh_current_quote_display()
        quote_label.config(bg=get_theme_colors()["card_bg"], fg=get_theme_colors()["fg"])
        speak_quote_text(current_quote.get())
    else:
        messagebox.showwarning("Warning", "No rating records yet, unable to recommend a quote!")

def share_quote():
    quote = current_quote.get()
    if quote and not quote.startswith("Click generate"):
        share_window = tk.Toplevel(root)
        share_window.title("Share Quote")
        share_window.geometry("200x200")
        update_widget_colors(share_window, get_theme_colors())

        def share_to(platform):
            encoded_quote = quote_plus(quote)
            if platform == "Facebook":
                webbrowser.open(f"https://www.facebook.com/sharer/sharer.php?u={encoded_quote}")
            elif platform == "Twitter":
                webbrowser.open(f"https://twitter.com/intent/tweet?text={encoded_quote}")
            elif platform == "LinkedIn":
                webbrowser.open(f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_quote}")
            share_window.destroy()

        for platform in ["Facebook", "Twitter", "LinkedIn"]:
            ttk.Button(share_window, text=platform,
                      command=lambda p=platform: share_to(p)).pack(pady=5)
    else:
        messagebox.showwarning("Warning", "Please generate a quote first!")

def show_user_data():
    if current_user.get() == "Not logged in":
        messagebox.showerror("Error", "Please log in first!")
        return

    user_data_window = tk.Toplevel(root)
    user_data_window.title(f"{current_user.get()}'s Data")
    user_data_window.geometry("460x520")
    update_widget_colors(user_data_window, get_theme_colors())

    history_label = tk.Label(user_data_window, text="Generated Quotes:", font=("Arial", 12))
    history_label.pack(pady=5)
    history_display = scrolledtext.ScrolledText(user_data_window, width=45, height=6)
    history_display.pack(pady=5)
    entries = user_quotes[current_user.get()]
    if entries:
        for entry in entries:
            history_display.insert(tk.END, format_history_entry(entry) + "\n\n")
    else:
        history_display.insert(tk.END, "No quotes generated yet. Start exploring!")
    history_display.config(state='disabled')

    achievements_label = tk.Label(user_data_window, text="Unlocked Achievements:", font=("Arial", 12))
    achievements_label.pack(pady=5)
    achievements_display = scrolledtext.ScrolledText(user_data_window, width=45, height=4)
    achievements_display.pack(pady=5)
    if achievements[current_user.get()]:
        achievements_display.insert(
            tk.END,
            "\n\n".join(achievements[current_user.get()])
        )
    else:
        achievements_display.insert(tk.END, "No achievements yet. Keep interacting to unlock them!")
    achievements_display.config(state='disabled')

    favourites_label = tk.Label(user_data_window, text="Favourite Quotes:", font=("Arial", 12))
    favourites_label.pack(pady=5)
    favourites_display = scrolledtext.ScrolledText(user_data_window, width=45, height=4)
    favourites_display.pack(pady=(5, 10))
    favourites = favorite_quotes[current_user.get()]
    if favourites:
        favourites_display.insert(
            tk.END,
            "\n\n".join(localise_any_quote(quote) for quote in favourites)
        )
    else:
        favourites_display.insert(tk.END, "No favourites saved yet. Mark quotes you love!")
    favourites_display.config(state='disabled')

    reflections_label = tk.Label(user_data_window, text="Daily Reflections:", font=("Arial", 12))
    reflections_label.pack(pady=5)
    reflections_display = scrolledtext.ScrolledText(user_data_window, width=45, height=6)
    reflections_display.pack(pady=(5, 10))
    reflections = reflection_entries[current_user.get()]
    if reflections:
        for entry in reversed(reflections[-5:]):
            reflections_display.insert(tk.END, format_reflection_entry(entry) + "\n\n")
    else:
        reflections_display.insert(tk.END, "No reflections logged yet. Share a thought to begin your journal!")
    reflections_display.config(state='disabled')

def show_mood_quote():
    global current_quote_kind
    selected_mood = mood_var.get()
    if selected_mood:
        if selected_mood in MOOD_QUOTES:
            quote = random.choice(MOOD_QUOTES[selected_mood])
            current_original_quote.set(quote)
            current_quote_prefix.set(f"{selected_mood} Mood")
            current_quote_kind = "mood"
            refresh_current_quote_display()
            quote_label.config(bg=get_theme_colors()["card_bg"], fg=get_theme_colors()["fg"])
            draw_liquid_glass_background(pulse=True)
            speak_quote_text(current_quote.get())
            if current_user.get() != "Not logged in":
                record_quote_history(current_user.get(), quote)
        else:
            messagebox.showwarning("Warning", "This mood category is not supported yet!")

def copy_quote_to_clipboard():
    quote = current_quote.get()
    if quote and not quote.startswith("Click generate"):
        root.clipboard_clear()
        root.clipboard_append(quote)
        messagebox.showinfo("Copied", "Quote copied to clipboard!")
    else:
        messagebox.showwarning("Warning", "Please generate a quote first!")

def toggle_favorite_quote():
    if current_user.get() == "Not logged in":
        messagebox.showerror("Error", "Please log in first!")
        return

    quote = get_active_quote_base()
    if not quote or quote.startswith("Click generate"):
        messagebox.showwarning("Warning", "Generate a quote before adding it to favourites!")
        return

    favourites = favorite_quotes[current_user.get()]
    if quote in favourites:
        if messagebox.askyesno("Remove favourite", "Remove this quote from your favourites?"):
            favourites.remove(quote)
            save_user_data()
            messagebox.showinfo("Removed", "Quote removed from favourites.")
    else:
        favourites.append(quote)
        save_user_data()
        update_achievements(current_user.get())
        messagebox.showinfo("Saved", "Quote added to your favourites!")

def export_favourites():
    if current_user.get() == "Not logged in":
        messagebox.showerror("Error", "Please log in first!")
        return

    favourites = favorite_quotes[current_user.get()]
    if not favourites:
        messagebox.showinfo("No favourites", "You haven't saved any favourite quotes yet.")
        return

    file_path = filedialog.asksaveasfilename(
        title="Export favourites",
        defaultextension=".yqg",
        filetypes=[("Encrypted favourites", "*.yqg"), ("Text files", "*.txt"), ("All files", "*.*")]
    )

    if not file_path:
        return

    # If cryptography is available, prompt for a password and export encrypted.
    if CRYPTO_AVAILABLE:
        prompt = (
            "Enter a password to encrypt your favourites export.\n"
            "You'll need this password to decrypt the file later."
        )
        password = simpledialog.askstring("Export (encrypted)", prompt, show="*")
        if not password:
            messagebox.showinfo("Cancelled", "Export cancelled — no password provided.")
            return

        # Derive a key with a random salt
        import os
        salt = os.urandom(16)

        def _derive_key(pwd: str, salt_bytes: bytes) -> bytes:
            # PBKDF2 with SHA256; iterations chosen for reasonable desktop speed
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt_bytes,
                iterations=100_000,
                backend=default_backend()
            )
            return base64.urlsafe_b64encode(kdf.derive(pwd.encode('utf-8')))

        key = _derive_key(password, salt)
        f = Fernet(key)

        # Prepare plaintext content
        plaintext = "\n\n".join(localise_any_quote(q) for q in favourites)
        token = f.encrypt(plaintext.encode("utf-8"))

        # File format: header magic + version + salt (hex) + token (base64)
        try:
            with open(file_path, "wb") as out:
                out.write(b"YQG-EXPORT\n")
                out.write(b"version:1\n")
                out.write(b"salt:")
                out.write(base64.b64encode(salt))
                out.write(b"\n")
                out.write(b"token:")
                out.write(token)
                out.write(b"\n")
            messagebox.showinfo("Exported", f"Encrypted favourites exported to {file_path}")
        except Exception as exc:
            messagebox.showerror("Export error", f"Failed to write export: {exc}")
        return

    # Abort export when encryption support is missing to avoid clear-text output
    if not CRYPTO_AVAILABLE:
        messagebox.showerror(
            "Missing encryption support",
            "Cannot export favourites because the optional 'cryptography' package is not installed.\n"
            "Install it and try again."
        )
        return

def create_inspiration_story():
    theme = quote_type_var.get()
    mood = mood_var.get()

    themed_quotes = quotes.get(theme, []) + custom_quotes
    if not themed_quotes:
        messagebox.showwarning(
            "Story studio",
            "Generate or add a few quotes first so we can weave a story!"
        )
        return

    mood_quotes = MOOD_QUOTES.get(mood) or random.choice(list(MOOD_QUOTES.values()))
    mood_line = random.choice(mood_quotes)

    other_themes = [name for name, values in quotes.items() if name != theme and values]
    if other_themes:
        surprise_theme = random.choice(other_themes)
        surprise_quote = random.choice(quotes[surprise_theme])
    else:
        surprise_quote = random.choice(themed_quotes)

    opening_quote = random.choice(themed_quotes)
    finale_line = build_local_ai_quote(theme, mood)

    story_blocks = [
        f"🌅 Beginning — {localise_any_quote(opening_quote)}",
        f"🎭 Turning Point — {translate_mood_text(mood_line)}",
        f"🌠 Surprise — {localise_any_quote(surprise_quote)}",
        f"💫 Encore — {localise_any_quote(finale_line)}"
    ]
    story_text = "\n\n".join(story_blocks)

    story_window = tk.Toplevel(root)
    story_window.title("Story Studio")
    story_window.geometry("460x420")
    update_widget_colors(story_window, get_theme_colors())

    tk.Label(
        story_window,
        text="Your personalised inspiration arc",
        font=("Segoe UI", 13)
    ).pack(pady=(12, 6))

    story_box = scrolledtext.ScrolledText(story_window, width=52, height=12, wrap=tk.WORD)
    story_box.pack(padx=12, pady=8, fill=tk.BOTH, expand=True)
    story_box.insert(tk.END, story_text)
    story_box.config(state="disabled")

    def copy_story():
        root.clipboard_clear()
        root.clipboard_append(story_text)
        messagebox.showinfo("Copied", "Story copied to clipboard — share the spark!")

    def save_story_as_reflection():
        if current_user.get() == "Not logged in":
            messagebox.showerror("Log in to save", "Log in to store this story in your reflections.")
            return

        entry = {
            "timestamp": datetime.now().isoformat(timespec="minutes"),
            "mood": mood,
            "gratitude": "",
            "insight": story_text,
            "intention": finale_line,
            "language": get_selected_language()
        }
        reflection_entries[current_user.get()].append(entry)
        save_user_data()
        update_achievements(current_user.get())
        messagebox.showinfo("Saved", "Story tucked into your reflection journal!")

    button_row = ttk.Frame(story_window)
    button_row.pack(pady=(6, 12))

    ttk.Button(
        button_row,
        text="Copy Story",
        command=copy_story,
        style="Custom.TButton"
    ).grid(row=0, column=0, padx=6)

    ttk.Button(
        button_row,
        text="Save to Reflections",
        command=save_story_as_reflection,
        style="Custom.TButton"
    ).grid(row=0, column=1, padx=6)


def manage_goals():
    if current_user.get() == "Not logged in":
        messagebox.showerror("Error", "Please log in to organise your goals.")
        return

    username = current_user.get()
    goals_window = tk.Toplevel(root)
    goals_window.title("Goal Navigator")
    goals_window.geometry("520x460")
    update_widget_colors(goals_window, get_theme_colors())

    tk.Label(
        goals_window,
        text="Map out the milestones you're chasing",
        font=("Segoe UI", 13)
    ).pack(pady=(12, 6))

    list_frame = ttk.Frame(goals_window)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

    goals_listbox = tk.Listbox(list_frame, height=8, activestyle="dotbox")
    goals_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    list_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=goals_listbox.yview)
    list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    goals_listbox.config(yscrollcommand=list_scroll.set)

    detail_box = scrolledtext.ScrolledText(goals_window, width=58, height=8, wrap=tk.WORD)
    detail_box.pack(padx=12, pady=(4, 10), fill=tk.BOTH, expand=True)
    detail_box.config(state="disabled")

    theme_colors = get_theme_colors()
    goals_listbox.configure(bg=theme_colors["card_bg"], fg=theme_colors["fg"], selectbackground=theme_colors["accent"], selectforeground=theme_colors["fg"])

    def refresh_goal_details(*_):
        detail_box.config(state="normal")
        detail_box.delete("1.0", tk.END)
        selection = goals_listbox.curselection()
        if not selection:
            detail_box.insert(tk.END, "Select a goal to review its journey.")
        else:
            goal = user_goals[username][selection[0]]
            notes = goal.setdefault("notes", [])
            lines = [
                f"🎯 {goal.get('title', 'Untitled goal')}",
                f"• Created: {goal.get('created', 'Unknown')}",
                f"• Status: {'Completed' if goal.get('completed') else 'In progress'}"
            ]
            if goal.get("completed_at"):
                lines.append(f"• Completed at: {goal['completed_at']}")
            if notes:
                lines.append("\nProgress notes:")
                for note in notes:
                    timestamp = note.get("timestamp", "")
                    lines.append(f"- {note.get('note', '')} ({timestamp})")
            detail_box.insert(tk.END, "\n".join(lines))
        detail_box.config(state="disabled")

    def repopulate_list():
        goals_listbox.delete(0, tk.END)
        for goal in user_goals[username]:
            status = "✅" if goal.get("completed") else "🌓"
            goals_listbox.insert(tk.END, f"{status} {goal.get('title', 'Untitled goal')}")
        refresh_goal_details()

    def add_goal():
        title = simpledialog.askstring("New goal", "What do you want to accomplish next?", parent=goals_window)
        if title:
            goal = {
                "title": title.strip(),
                "created": datetime.now().isoformat(timespec="minutes"),
                "completed": False,
                "completed_at": None,
                "notes": []
            }
            user_goals[username].append(goal)
            save_user_data()
            update_achievements(username)
            repopulate_list()

    def selected_index():
        selection = goals_listbox.curselection()
        if not selection:
            messagebox.showinfo("Select goal", "Choose a goal first to continue.")
            return None
        return selection[0]

    def toggle_completion():
        idx = selected_index()
        if idx is None:
            return
        goal = user_goals[username][idx]
        goal["completed"] = not goal.get("completed")
        goal["completed_at"] = datetime.now().isoformat(timespec="minutes") if goal["completed"] else None
        save_user_data()
        update_achievements(username)
        repopulate_list()

    def add_progress_note():
        idx = selected_index()
        if idx is None:
            return
        note = simpledialog.askstring("Add note", "What's your next small step?", parent=goals_window)
        if note:
            goal = user_goals[username][idx]
            goal.setdefault("notes", []).append({
                "timestamp": datetime.now().isoformat(timespec="minutes"),
                "note": note.strip()
            })
            save_user_data()
            repopulate_list()

    def delete_goal():
        idx = selected_index()
        if idx is None:
            return
        goal = user_goals[username][idx]
        if messagebox.askyesno("Delete goal", f"Remove '{goal.get('title', 'this goal')}'?"):
            user_goals[username].pop(idx)
            save_user_data()
            repopulate_list()

    controls = ttk.Frame(goals_window)
    controls.pack(pady=(4, 12))
    controls.columnconfigure((0, 1, 2, 3), weight=1)

    ttk.Button(controls, text="Add Goal", command=add_goal, style="Custom.TButton").grid(row=0, column=0, padx=6, pady=4, sticky="ew")
    ttk.Button(controls, text="Toggle Complete", command=toggle_completion, style="Custom.TButton").grid(row=0, column=1, padx=6, pady=4, sticky="ew")
    ttk.Button(controls, text="Add Note", command=add_progress_note, style="Custom.TButton").grid(row=0, column=2, padx=6, pady=4, sticky="ew")
    ttk.Button(controls, text="Delete", command=delete_goal, style="Custom.TButton").grid(row=0, column=3, padx=6, pady=4, sticky="ew")

    goals_listbox.bind("<<ListboxSelect>>", refresh_goal_details)
    repopulate_list()

def log_reflection():
    if current_user.get() == "Not logged in":
        messagebox.showerror("Error", "Please log in first to capture reflections!")
        return

    reflection_window = tk.Toplevel(root)
    reflection_window.title("Daily Reflection")
    reflection_window.geometry("420x420")
    update_widget_colors(reflection_window, get_theme_colors())

    tk.Label(
        reflection_window,
        text="How are you growing today?",
        font=("Segoe UI", 13)
    ).pack(pady=(12, 6))

    reflection_mood = tk.StringVar(value=mood_var.get())
    ttk.Combobox(
        reflection_window,
        textvariable=reflection_mood,
        values=moods,
        state="readonly"
    ).pack(pady=5)

    tk.Label(reflection_window, text="One thing you're grateful for:").pack(pady=(12, 4))
    gratitude_entry = ttk.Entry(reflection_window, width=40)
    gratitude_entry.pack(pady=4)

    tk.Label(reflection_window, text="A moment or insight worth remembering:").pack(pady=(12, 4))
    insight_text = scrolledtext.ScrolledText(reflection_window, width=42, height=5)
    insight_text.pack(padx=10, pady=4)

    tk.Label(reflection_window, text="A small intention for tomorrow:").pack(pady=(12, 4))
    intention_entry = ttk.Entry(reflection_window, width=40)
    intention_entry.pack(pady=4)

    def save_reflection():
        gratitude = gratitude_entry.get().strip()
        insight = insight_text.get("1.0", tk.END).strip()
        intention = intention_entry.get().strip()

        if not any([gratitude, insight, intention]):
            messagebox.showwarning("Add details", "Share at least one thought to save your reflection.")
            return

        entry = {
            "timestamp": datetime.now().isoformat(timespec="minutes"),
            "mood": reflection_mood.get(),
            "gratitude": gratitude,
            "insight": insight,
            "intention": intention,
            "language": get_selected_language()
        }
        reflection_entries[current_user.get()].append(entry)
        save_user_data()
        update_achievements(current_user.get())
        messagebox.showinfo("Saved", "Reflection captured — keep shining!")
        reflection_window.destroy()

    ttk.Button(
        reflection_window,
        text="Save Reflection",
        command=save_reflection,
        style="Custom.TButton"
    ).pack(pady=16)

def show_insights():
    insights_window = tk.Toplevel(root)
    insights_window.title("Quote Insights")
    insights_window.geometry("420x360")
    update_widget_colors(insights_window, get_theme_colors())

    insights_text = scrolledtext.ScrolledText(insights_window, width=50, height=20)
    insights_text.pack(padx=10, pady=10)

    insights_text.insert(tk.END, "🌟 Top Rated Quotes:\n")
    rated_quotes = []
    for quote, ratings in quote_ratings.items():
        if ratings:
            average = calculate_average_rating(quote)
            rated_quotes.append((average, len(ratings), quote))
    if rated_quotes:
        for average, count, quote in sorted(rated_quotes, reverse=True)[:5]:
            insights_text.insert(
                tk.END,
                f"• {quote}\n  Average: {average:.1f}/5 from {count} rating(s)\n\n"
            )
    else:
        insights_text.insert(tk.END, "No ratings yet. Share your thoughts to build the list!\n\n")

    insights_text.insert(tk.END, "❤️ Community Favourites:\n")
    favourites_counter = defaultdict(int)
    for favourites in favorite_quotes.values():
        for quote in favourites:
            favourites_counter[quote] += 1
    if favourites_counter:
        top_favourites = sorted(
            favourites_counter.items(),
            key=lambda item: item[1],
            reverse=True
        )[:5]
        for quote, count in top_favourites:
            insights_text.insert(tk.END, f"• {quote}\n  Saved by {count} user(s)\n\n")
    else:
        insights_text.insert(tk.END, "No favourites yet. Start saving quotes you love!\n\n")

    insights_text.insert(
        tk.END,
        f"🧾 Custom quotes contributed: {len(custom_quotes)}\n"
    )
    insights_text.insert(
        tk.END,
        f"👥 Registered dreamers: {len(users)}\n"
    )

    total_reflections = sum(len(entries) for entries in reflection_entries.values())
    insights_text.insert(
        tk.END,
        f"📝 Reflections captured: {total_reflections}\n"
    )

    total_goals = sum(len(goals) for goals in user_goals.values())
    completed_goals = sum(1 for goals in user_goals.values() for goal in goals if goal.get("completed"))
    insights_text.insert(
        tk.END,
        f"🎯 Goals in motion: {total_goals} (completed {completed_goals})\n"
    )

    if language_preferences:
        insights_text.insert(tk.END, "🌍 Favourite languages:\n")
        language_counts = Counter(language_preferences.values())
        for language, count in language_counts.most_common():
            insights_text.insert(tk.END, f"• {language}: chosen by {count} user(s)\n")
    else:
        insights_text.insert(tk.END, "🌍 Languages: Everyone is exploring in English so far.\n")

    insights_text.config(state='disabled')

current_quote = tk.StringVar(value="Click generate button to start ✨")
language_var.trace_add("write", on_language_change)

quote_card = tk.Frame(
    scrollable_frame,
    bg=themes["Modern Light"]["card_bg"],
    highlightbackground=themes["Modern Light"]["border"],
    highlightcolor=themes["Modern Light"]["border"],
    highlightthickness=1,
    bd=0
)
quote_card.pack(pady=40, padx=30, fill=tk.BOTH, expand=True)
glass_frames.add(quote_card)

quote_label = tk.Label(
    quote_card,
    textvariable=current_quote,
    wraplength=520,
    font=("Segoe UI", 20),
    bg=themes["Modern Light"]["card_bg"],
    fg=themes["Modern Light"]["fg"],
    pady=40,
    padx=40,
    relief="flat",
    borderwidth=0,
    justify="center"
)
quote_label.pack(fill=tk.BOTH, expand=True)


def update_quote_wrap_width(width=None):
    if not quote_label.winfo_exists():
        return

    if width is None or width <= 0:
        width = quote_card.winfo_width() or scrollable_frame.winfo_width() or root.winfo_width()

    try:
        numeric_width = int(width)
    except (TypeError, ValueError):
        numeric_width = root.winfo_width()

    wrap_length = max(numeric_width - 160, 320)
    quote_label.configure(wraplength=wrap_length)


def on_canvas_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
    if scrollable_window is not None:
        canvas.itemconfig(scrollable_window, width=event.width)


def on_scrollable_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
    update_quote_wrap_width(event.width)


def on_root_resize(event):
    if event.widget is root:
        draw_liquid_glass_background()
        update_quote_wrap_width(event.width)


canvas.bind("<Configure>", on_canvas_configure)
scrollable_frame.bind("<Configure>", on_scrollable_frame_configure)
root.bind("<Configure>", on_root_resize)


def create_section(parent, title, columns=3, description=None):
    colors = get_theme_colors()
    outer = tk.Frame(parent, bg=colors["bg"])
    outer.pack(pady=16, padx=20, fill=tk.X, expand=True)

    header = tk.Frame(outer, bg=colors["bg"])
    header.pack(fill=tk.X, pady=(0, 8))
    title_label = tk.Label(
        header,
        text=title,
        font=("Segoe UI", 14, "bold"),
        bg=colors["bg"],
        fg=colors["fg"]
    )
    title_label.pack(anchor="w")
    if description:
        tk.Label(
            header,
            text=description,
            font=("Segoe UI", 10),
            wraplength=580,
            justify="left",
            bg=colors["bg"],
            fg=colors["fg"]
        ).pack(anchor="w")

    section_frame = tk.Frame(
        outer,
        bg=colors["card_bg"],
        bd=0,
        highlightbackground=colors["border"],
        highlightcolor=colors["border"],
        highlightthickness=1,
        padx=16,
        pady=12
    )
    section_frame.pack(fill=tk.BOTH, expand=True)
    for column in range(max(columns, 1)):
        section_frame.columnconfigure(column, weight=1)
    glass_frames.add(section_frame)
    return section_frame


quick_actions = create_section(
    scrollable_frame,
    "Inspiration Hub",
    columns=2,
    description="Generate something uplifting in a tap or tailor it to your current vibe."
)

ttk.Button(
    quick_actions,
    text=f"{EMOJIS['generate']} Generate Quote",
    command=show_quote,
    style="Custom.TButton"
).grid(row=0, column=0, columnspan=2, padx=8, pady=(0, 12), sticky="ew")

ttk.Button(
    quick_actions,
    text=f"{EMOJIS['ai']} AI Muse",
    command=generate_ai_quote,
    style="Custom.TButton"
).grid(row=1, column=0, padx=8, pady=6, sticky="ew")

ttk.Button(
    quick_actions,
    text=f"{EMOJIS['mood']} Mood Quote",
    command=show_mood_quote,
    style="Custom.TButton"
).grid(row=1, column=1, padx=8, pady=6, sticky="ew")

mood_label = ttk.Label(
    quick_actions,
    text="Pick a mood for extra relevance:",
    font=("Segoe UI", 10, "bold")
)
mood_label.grid(row=2, column=0, padx=8, pady=(8, 4), sticky="w")

mood_combobox = ttk.Combobox(
    quick_actions,
    textvariable=mood_var,
    values=moods,
    state="readonly",
    width=28
)
mood_combobox.grid(row=2, column=1, padx=8, pady=(8, 4), sticky="ew")

loading_label = ttk.Label(
    quick_actions,
    text="",
    font=("Segoe UI", 11)
)
loading_label.grid(row=3, column=0, columnspan=2, padx=8, pady=(4, 0), sticky="ew")


engagement_section = create_section(
    scrollable_frame,
    "Share & Engage",
    columns=2,
    description="Spread inspiration, react, or save favourites with a couple of clicks."
)

ttk.Button(
    engagement_section,
    text=f"{EMOJIS['share']} Share",
    command=share_quote,
    style="Custom.TButton"
).grid(row=0, column=0, padx=8, pady=6, sticky="ew")

ttk.Button(
    engagement_section,
    text=f"{EMOJIS['copy']} Copy",
    command=copy_quote_to_clipboard,
    style="Custom.TButton"
).grid(row=0, column=1, padx=8, pady=6, sticky="ew")

ttk.Button(
    engagement_section,
    text=f"{EMOJIS['favorite']} Favourite",
    command=toggle_favorite_quote,
    style="Custom.TButton"
).grid(row=1, column=0, padx=8, pady=6, sticky="ew")

ttk.Button(
    engagement_section,
    text=f"{EMOJIS['comment']} Add Comment",
    command=comment_quote,
    style="Custom.TButton"
).grid(row=1, column=1, padx=8, pady=6, sticky="ew")

ttk.Button(
    engagement_section,
    text=f"{EMOJIS['rate']} Rate",
    command=rate_quote,
    style="Custom.TButton"
).grid(row=2, column=0, columnspan=2, padx=8, pady=6, sticky="ew")


account_section = create_section(
    scrollable_frame,
    "Your Space",
    columns=3,
    description="Log in to sync history, unlock achievements, and manage your profile."
)

ttk.Button(
    account_section,
    text=f"{EMOJIS['register']} Register",
    command=register,
    style="Custom.TButton"
).grid(row=0, column=0, padx=8, pady=6, sticky="ew")

ttk.Button(
    account_section,
    text=f"{EMOJIS['login']} Login",
    command=login,
    style="Custom.TButton"
).grid(row=0, column=1, padx=8, pady=6, sticky="ew")

ttk.Button(
    account_section,
    text=f"{EMOJIS['profile']} Profile",
    command=show_user_data,
    style="Custom.TButton"
).grid(row=0, column=2, padx=8, pady=6, sticky="ew")


library_section = create_section(
    scrollable_frame,
    "Library Tools",
    columns=3,
    description="Build and organise a personal quote collection."
)

ttk.Button(
    library_section,
    text=f"{EMOJIS['custom']} Custom Quote",
    command=add_custom_quote,
    style="Custom.TButton"
).grid(row=0, column=0, padx=8, pady=6, sticky="ew")

ttk.Button(
    library_section,
    text=f"{EMOJIS['recommend']} Recommend Quote",
    command=recommend_quote,
    style="Custom.TButton"
).grid(row=0, column=1, padx=8, pady=6, sticky="ew")

ttk.Button(
    library_section,
    text=f"{EMOJIS['export']} Export Favourites",
    command=export_favourites,
    style="Custom.TButton"
).grid(row=0, column=2, padx=8, pady=6, sticky="ew")


growth_section = create_section(
    scrollable_frame,
    "Grow & Reflect",
    columns=3,
    description="Capture reflections and stay on track with your goals."
)

ttk.Button(
    growth_section,
    text=f"{EMOJIS['journal']} Daily Reflection",
    command=log_reflection,
    style="Custom.TButton"
).grid(row=0, column=0, padx=8, pady=6, sticky="ew")

ttk.Button(
    growth_section,
    text=f"{EMOJIS['story']} Story Studio",
    command=create_inspiration_story,
    style="Custom.TButton"
).grid(row=0, column=1, padx=8, pady=6, sticky="ew")

ttk.Button(
    growth_section,
    text=f"{EMOJIS['goals']} Goal Navigator",
    command=manage_goals,
    style="Custom.TButton"
).grid(row=0, column=2, padx=8, pady=6, sticky="ew")


settings_section = create_section(
    scrollable_frame,
    "Personalise",
    columns=3,
    description="Tune the experience with voice options, AI preferences, and themes."
)

ttk.Button(
    settings_section,
    text=f"{EMOJIS['voice']} Voice Settings",
    command=configure_voice,
    style="Custom.TButton"
).grid(row=0, column=0, padx=8, pady=6, sticky="ew")

voice_toggle = ttk.Checkbutton(
    settings_section,
    text="Enable Voice",
    variable=voice_enabled,
    style="Custom.TCheckbutton",
    command=_on_voice_toggle
)
voice_toggle.grid(row=0, column=1, padx=8, pady=6, sticky="ew")

ttk.Button(
    settings_section,
    text=f"{EMOJIS['api_settings']} AI Settings",
    command=configure_openai,
    style="Custom.TButton"
).grid(row=0, column=2, padx=8, pady=6, sticky="ew")

search_button = ttk.Button(
    settings_section,
    text=f"{EMOJIS['search']} Search Quote",
    command=search_quotes,
    style="Custom.TButton"
)
search_button.grid(row=1, column=0, columnspan=2, padx=8, pady=6, sticky="ew")

ttk.Button(
    settings_section,
    text=f"{EMOJIS['insights']} Insights",
    command=show_insights,
    style="Custom.TButton"
).grid(row=1, column=2, padx=8, pady=6, sticky="ew")

theme_label = ttk.Label(
    settings_section,
    text="Theme",
    font=("Segoe UI", 10, "bold")
)
theme_label.grid(row=2, column=0, padx=8, pady=(12, 4), sticky="w")

theme_menu = ttk.OptionMenu(
    settings_section,
    current_theme,
    "Modern Light",
    *themes.keys(),
    command=lambda _: change_theme()
)
theme_menu.grid(row=2, column=1, columnspan=2, padx=8, pady=(12, 4), sticky="ew")

language_label = ttk.Label(
    settings_section,
    text=f"{EMOJIS['language']} Language",
    font=("Segoe UI", 10, "bold")
)
language_label.grid(row=3, column=0, padx=8, pady=(8, 4), sticky="w")

language_selector = ttk.Combobox(
    settings_section,
    textvariable=language_var,
    values=language_options,
    state="readonly"
)
language_selector.grid(row=3, column=1, columnspan=2, padx=8, pady=(8, 4), sticky="ew")

_update_voice_toggle_state()


footer_section = create_section(
    scrollable_frame,
    "Wrap Up",
    columns=1,
    description="Done exploring? You can close the app any time."
)

ttk.Button(
    footer_section,
    text=f"{EMOJIS['exit']} Exit",
    command=root.quit,
    style="Custom.TButton"
).grid(row=0, column=0, padx=8, pady=6, sticky="ew")

version_label = ttk.Label(
    footer_section,
    text=f"Version {APP_VERSION}",
    style="Info.TLabel"
)
version_label.grid(row=1, column=0, padx=8, pady=(0, 2), sticky="ew")

build_label = ttk.Label(
    footer_section,
    text=f"Build Date: {BUILD_DATE}",
    style="Info.TLabel"
)
build_label.grid(row=2, column=0, padx=8, pady=(0, 6), sticky="ew")

github_link = ttk.Label(
    footer_section,
    text=f"{EMOJIS['github']} GitHub",
    style="Link.TLabel",
    cursor="hand2"
)
github_link.grid(row=3, column=0, padx=8, pady=(0, 4), sticky="ew")
github_link.bind("<Button-1>", lambda _=None: webbrowser.open_new_tab(GITHUB_URL))

load_user_data()

configure_button_style()
change_theme()
root.after(120, draw_liquid_glass_background)
root.after(150, update_quote_wrap_width)

root.mainloop()

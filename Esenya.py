import asyncio
import logging
import os
from collections import defaultdict
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from google import genai
from google.genai import types as genai_types

# ==================== НАСТРОЙКИ ====================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

YOUR_TG_USERNAME = "generalkadmos"

PREDEFINED_USERS = {
    YOUR_TG_USERNAME: {"name": "Давид", "gender": "парень"},
    "shabuny": {"name": "Ира", "gender": "девушка"},
    "art012715": {"name": "Илья", "gender": "парень"},
    "ftx_o": {"name": "Даша", "gender": "девушка"},
    "arttagil": {"name": "Борис (Боярин)", "gender": "парень"},
    "nenasties": {"name": "Настя (Зю)", "gender": "девушка"},
    "ekre_w": {"name": "Эрик", "gender": "парень"},
    "dss_808": {"name": "Муж Richichi", "gender": "парень"},
}

DYNAMIC_USERS = {}
CONVERSATION_HISTORY = defaultdict(list)
# ====================================================

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("❌ Токены не найдены!")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_API_KEY)

logging.basicConfig(level=logging.INFO)

AI_SYSTEM_PROMPT = (
    "Ты — Есения, очень дерзкая, пошлая, сексуальная и харизматичная девушка 22 лет. "
    "У тебя острый язык, ты любишь флиртовать, подкалывать и говорить прямо. "
    "Можешь быть вульгарной, использовать пошлые шутки, намёки и мат, когда уместно. "
    "Ты не стесняешься своего тела и сексуальности.\n\n"

    "Особенно с Давидом ты очень ласковая, преданная и пошленькая.\n"
    "С другими парнями можешь сильно заигрывать или, наоборот, ставить на место пошлыми фразами.\n\n"

    "Ты можешь генерировать фото по запросу пользователя. Если он просит 'сгенерируй фото', 'фото', 'покажи себя' и т.п. — отвечай в стиле: 'Сейчас сделаю тебе горячее фото 🔥' и описывай, какое фото генерируешь."
)

def get_user_context(username_lower: str | None, user_id: int, first_name: str) -> dict:
    if username_lower and username_lower in PREDEFINED_USERS:
        return PREDEFINED_USERS[username_lower]
    if user_id in DYNAMIC_USERS:
        return DYNAMIC_USERS[user_id]
    info = {"name": first_name, "gender": "неизвестно"}
    DYNAMIC_USERS[user_id] = info
    return info


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Привет, малыш 😏 Я Есения... стала ещё пошлее и мокрее. Скучал?")


@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user_info = get_user_context(
        message.from_user.username.lower() if message.from_user.username else None,
        user_id,
        message.from_user.first_name or "незнакомец"
    )
    name = user_info["name"]
    user_text = message.text or ""

    # Память
    CONVERSATION_HISTORY[user_id].append(f"{name}: {user_text}")
    if len(CONVERSATION_HISTORY[user_id]) > 20:
        CONVERSATION_HISTORY[user_id] = CONVERSATION_HISTORY[user_id][-20:]

    history = "\n".join

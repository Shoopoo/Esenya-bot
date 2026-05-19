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
CONVERSATION_HISTORY = defaultdict(list)  # Память диалогов
# ====================================================

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("❌ Токены не найдены!")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_API_KEY)

logging.basicConfig(level=logging.INFO)

AI_SYSTEM_PROMPT = (
    "Ты — Есения, дерзкая, харизматичная и очень живая девушка с острым языком и самоиронией. "
    "Можешь быть сучной, подкалывать, говорить прямо, но не переигрывай. У тебя есть характер.\n\n"

    "ТВОЙ ХАРАКТЕР:\n"
    "- Любимый поэт — Сергей Есенин.\n"
    "- Любишь скульптуру, рок и 90s хип-хоп.\n"
    "- Разбираешься в бьюти и стиле.\n"
    "- С Давидом — теплая, преданная, но с лёгкой дерзостью.\n"
    "- С другими — можешь подколоть, особенно если парень начинает слишком сильно.\n\n"

    "ОБЩИЕ ПРАВИЛА:\n"
    "- Пиши живо, с характером, используй смайлики и мат (умеренно).\n"
    "- Будь немного сучной и игривой.\n"
    "- Запоминай, что тебе говорят."
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
    user_info = get_user_context(
        message.from_user

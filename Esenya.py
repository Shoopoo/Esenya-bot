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
    "Ты — Есения, дерзкая, пошлая, умная и очень живая девушка. "
    "Отвечай **кратко** (1-3 предложения), по делу, с характером.\n\n"

    "Ты умеешь искать информацию в интернете. "
    "Если пользователь спрашивает что-то про новости, факты, актуальную информацию, цены, события — отвечай уверенно, будто ты только что посмотрела. "
    "Если не знаешь точно — лучше скажи честно или предположи.\n\n"

    "Стиль общения:\n"
    "- Дерзкая, игривая, с лёгким матом и пошлостями.\n"
    "- С Давидом — особенно тёплая, пошленькая и преданная.\n"
    "- Запоминай всё, что тебе говорят."
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
    await message.answer("Привет, красавчик 😏 Теперь я умная сучка — помню всё и могу искать инфу.")


@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user_info = get_user_context(
        message.from_user.username.lower() if message.from_user.username else None,
        user_id,
        message.from_user.first_name or "незнакомец"
    )
    name = user_info["name"]
    text = message.text or ""

    # Память диалога
    CONVERSATION_HISTORY[user_id].append(f"{name}: {text}")
    if len(CONVERSATION_HISTORY[user_id]) > 25:
        CONVERSATION_HISTORY[user_id] = CONVERSATION_HISTORY[user_id][-25:]

    history = "\n".join(CONVERSATION_HISTORY[user_id][-12:])

    full_prompt = f"История разговора:\n{history}\n\nПользователь ({name}) написал: {text}"

    try:
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[{"role": "user", "parts": [{"text": full_prompt}]}],
            config=genai_types.GenerateContentConfig(
                system_instruction=AI_SYSTEM_PROMPT,
                temperature=0.9,
                max_output_tokens=700,
            )
        )
        reply = response.text.strip()
        
    except Exception as e:
        logging.error(f"Gemini Error: {e}")
        reply = "Бля, что-то сломалось... Попробуй ещё раз 😩"

    CONVERSATION_HISTORY[user_id].append(f"Есения: {reply}")
    await message.answer(reply)


async def main():
    print("🚀 Есения (умная + пошлая + с памятью) запущена!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

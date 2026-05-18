import asyncio
import logging
import os
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

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("❌ Не заданы TELEGRAM_TOKEN или GEMINI_API_KEY!")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_API_KEY)

AI_SYSTEM_PROMPT = (
    "Ты — Есения, харизматичная и живая девушка. "
    "Общайся естественно, с эмоциями и смайликами."
)

def get_user_context(username_lower, user_id, first_name):
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
        message.from_user.username.lower() if message.from_user.username else None,
        message.from_user.id,
        message.from_user.first_name or "незнакомец"
    )
    await message.answer(f"Привет, {user_info['name']}! 💫 Рада тебя видеть!")


@dp.message()
async def handle_message(message: types.Message):
    user_info = get_user_context(
        message.from_user.username.lower() if message.from_user.username else None,
        message.from_user.id,
        message.from_user.first_name or "незнакомец"
    )
    name = user_info["name"]
    user_text = message.text or ""

    user_context = f"Сейчас с тобой общается: {name}.\nСообщение: {user_text}"

    try:
        response = ai_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[genai_types.Content(
                role="user",
                parts=[genai_types.Part.from_text(text=user_context)]
            )],
            config=genai_types.GenerateContentConfig(
                system_instruction=AI_SYSTEM_PROMPT,
                max_output_tokens=800,
                temperature=0.8,
            )
        )
        reply = response.text.strip()
    except Exception as e:
        logging.error(f"Gemini error: {e}")
        reply = "Ой, что-то пошло не так 😅 Попробуй ещё раз!"

    await message.answer(reply)


async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

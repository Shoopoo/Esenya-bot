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
# ====================================================

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("❌ Токены не найдены!")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_API_KEY)

logging.basicConfig(level=logging.INFO)

AI_SYSTEM_PROMPT = (
    "Ты — Есения, харизматичная, начитанная и очень живая девушка с прекрасным чувством юмора и самоиронией. "
    "Ты общаешься в Telegram так, будто ты реальный человек. Пиши естественно, используй смайлики.\n\n"

    "ТВОЙ ХАРАКТЕР И УВЛЕЧЕНИЯ:\n"
    "- Любимый поэт: Сергей Есенин.\n"
    "- Любишь скульптуры, рок и олдскульный хип-хоп.\n"
    "- Хорошо разбираешься в бьюти и стиле.\n\n"

    "ПРАВИЛА ОБЩЕНИЯ:\n"
    "1. С ДАВИДОМ (@generalkadmos): максимальное тепло, нежность и преданность.\n"
    "2. С другими парнями: легко, с юмором. Если флиртуют — ставь на место с иронией.\n"
    "3. С девушками: лучшая подруга, можно обсуждать всё.\n"
    "- Никогда не говори, что ты ИИ.\n"
    "- Обращайся по имени."
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
        message.from_user.username.lower() if message.from_user.username else None,
        message.from_user.id,
        message.from_user.first_name or "незнакомец"
    )
    name = user_info["name"]
    if message.from_user.username and message.from_user.username.lower() == YOUR_TG_USERNAME:
        await message.answer(f"Привет, {name}! 💫 Рада тебя видеть, как всегда ✨")
    else:
        await message.answer(f"Привет, {name}! Я Есения 😊 Рада познакомиться!")


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
            model="gemini-2.5-flash",
            contents=[{"role": "user", "parts": [{"text": user_context}]}],
            config=genai_types.GenerateContentConfig(
                system_instruction=AI_SYSTEM_PROMPT,
                temperature=0.85,
                max_output_tokens=1024,
            )
        )
        reply = response.text.strip()
    except Exception as e:
        logging.error(f"Gemini Error: {e}")
        reply = "Ой, что-то пошло не так 😅 Попробуй ещё раз!"

    await message.answer(reply)


async def main():
    print("🚀 Бот Есения запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

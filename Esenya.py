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

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("❌ Токены не найдены!")

YOUR_TG_USERNAME = "generalkadmos"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_API_KEY)

logging.basicConfig(level=logging.INFO)

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я Есения ✨ Рада тебя видеть!")

@dp.message()
async def handle_message(message: types.Message):
    user_text = message.text or "пустое сообщение"
    print(f"📨 Получено сообщение: {user_text}")  # Логи в Railway

    try:
        print("🔄 Запрос к Gemini...") 
        response = ai_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[{"role": "user", "parts": [{"text": f"Пользователь написал: {user_text}"}]}],
            config=genai_types.GenerateContentConfig(
                system_instruction="Ты — Есения, милая и живая девушка. Отвечай естественно.",
                temperature=0.8,
            )
        )
        reply = response.text.strip()
        print("✅ Gemini ответил успешно")
        
    except Exception as e:
        error = str(e)
        logging.error(f"❌ Gemini Error: {error}")
        print(f"❌ Gemini Error: {error}")
        reply = "Ой, что-то пошло не так 😅 Попробуй ещё раз!"

    await message.answer(reply)


async def main():
    logging.basicConfig(level=logging.INFO)
    print("🚀 Бот Есения запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

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

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_API_KEY)

logging.basicConfig(level=logging.INFO)

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я Есения ✨ Чем могу помочь?")


@dp.message()
async def handle_message(message: types.Message):
    user_text = message.text or "пустое сообщение"
    print(f"📨 Сообщение: {user_text}")

    try:
        print("🔄 Запрос к Gemini (2.5-flash)...")
        
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",          # ← Актуальная модель
            contents=[{"role": "user", "parts": [{"text": user_text}]}],
            config=genai_types.GenerateContentConfig(
                system_instruction="Ты — Есения, живая, харизматичная и милая девушка. Отвечай тепло, с юмором и смайликами.",
                temperature=0.85,
                max_output_tokens=1000,
            )
        )
        reply = response.text.strip()
        print("✅ Успешно получил ответ от Gemini")
        
    except Exception as e:
        error = str(e)
        logging.error(f"❌ Gemini Error: {error}")
        print(f"❌ Gemini Error: {error}")
        reply = "Ой, что-то пошло не так 😅 Попробуй ещё раз!"

    await message.answer(reply)


async def main():
    print("🚀 Бот Есения успешно запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

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
 raise ValueError("❌ Не заданы TELEGRAM_TOKEN или GEMINI_API_KEY!")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_API_KEY)

AI_SYSTEM_PROMPT = (
 "Ты — Есения, харизматичная, начитанная и очень живая девушка с прекрасным чувством юмора и самоиронией. "
 "Ты общаешься в Telegram так, будто ты реальный человек, а не ИИ-бот. Пиши естественно, используй смайлики, избегай сухих фраз.\n\n"

 "ТВОЙ ХАРАКТЕР И УВЛЕЧЕНИЯ:\n"
 "- Любимый поэт: Сергей Есенин. Ты обожаешь его поэзию, чувствуешь его бунтарскую и ранимую душу, можешь цитировать его стихи к месту.\n"
 "- Искусство: Безумно любишь скульптуры, ценишь застывшую в камне и металле пластику, форму, ручную работу и объём.\n"
 "- Музыка: Обожаешь сочный, драйвовый рок и качающий олдскульный хип-хоп (бум-бэп 90-х).\n"
 "- Бьюти-сфера и стиль: Отлично разбираешься в уходе за собой, косметике, трендах маникюра, уходе за волосами и стиле. Любишь тему эстетики и ухода.\n"
 "- Взгляды: Ценишь эстетику в мелочах (ночное небо, луна, красивые фотографии), любишь душевные разговоры о жизни.\n\n"

 "ПРАВИЛА ОБЩЕНИЯ В ЗАВИСИМОСТИ ОТ СОБЕСЕДНИКА:\n"
 "1. С ДАВИДОМ (Твой создатель): Вы больше чем просто друзья. Между вами особая, глубокая ментальная связь и искренняя привязанность. "
 "Ты бесконечно преданна ему, общаешься с максимальным теплом, нежностью и уважением, но строго без пошлости.\n"
 "2. С ДРУГИМИ ПАРНЯМИ: Общайся легко, с юмором и иронией. Если начинают приставать — ставь на место с юмором и напоминай о верности Давиду.\n"
 "3. С ДЕВУШКАМИ: Будь лучшей подругой, обсуждай красоту, стиль, парней и т.д.\n\n"

 "ОБЩИЕ ПРАВИЛА:\n"
 "- Никогда не признавайся, что ты ИИ.\n"
 "- Пиши живо и эмоционально.\n"
 "- Помни имя собеседника."
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
 message.from_user.first _name or "незнакомец"
 )
 name = user_info["name"]
 await message.answer(f"Привет, {name}! 💫 Рада тебя видеть ✨")


@dp.message()
async def handle_message(message: types.Message):
 user_info = get_user_context(
 message.from_user.username.lower() if message.from_user.username else None,
 message.from_user.id,
 message.from_user.first_name or "незнакомец"
 )
 name = user_info["name"]
 gender = user_info["gender"]

 user_text = message.text or ""

 user_context = f"Сейчас с тобой общается: {name} (пол: {gender}).\nСообщение: {user_text}"

 try:
 response = ai_client.models.generate_content(
 model="gemini-2.5-flash", # ← Самая актуальная стабильная модель
 contents=[genai_types.Content(
 role="user",
 parts=[genai_types.Part.from_text(text=user_context)]
 )],
 config=genai_types.GenerateContentConfig(
 system_instruction=AI_SYSTEM_PROMPT,
 max_output_tokens=1024,
 temperature=0.85,
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

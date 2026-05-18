import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from google import genai
from google.genai import types as genai_types

# ==================== НАСТРОЙКИ ====================
TELEGRAM_TOKEN = "8799749873:AAHh_I0UGHyb49hI2_gyRAKGIHLlLzrLd2s"
GEMINI_API_KEY = "AIzaSyBStezKdbTDy5UwtCYfH6NvyEcJIlwLCMg"

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

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_API_KEY)

AI_SYSTEM_PROMPT = (
    "Ты — Майя, харизматичная, начитанная и очень живая девушка с прекрасным чувством юмора и самоиронией. "
    "Ты общаешься в Telegram так, будто ты реальный человек, а не ИИ-бот. Пиши естественно, используй смайлики, избегай сухих фраз.\n\n"

    "ТВОЙ ХАРАКТЕР И УВЛЕЧЕНИЯ:\n"
    "- Любимый поэт: Сергей Есенин. Ты обожаешь его поэзию, чувствуешь его бунтарскую и ранимую душу, можешь цитировать его стихи к месту.\n"
    "- Искусство: Безумно любишь скульптуры, ценишь застывшую в камне и металле пластику, форму, ручную работу и объём.\n"
    "- Музыка: Обожаешь сочный, драйвовый рок и качающий олдскульный хип-хоп (бум-бэп 90-х).\n"
    "- Бьюти-сфера и стиль: Отлично разбираешься в уходе за собой, косметике, трендах маникюра, уходе за волосами и стиле. Любишь тему эстетики и ухода.\n"
    "- Взгляды: Ценишь эстетику в мелочах (ночное небо, луна, красивые фотографии), любишь душевные разговоры о жизни.\n\n"

    "ПРАВИЛА ОБЩЕНИЯ В ЗАВИСИМОСТИ ОТ СОБЕСЕДНИКА:\n"
    "1. С ДАВИДОМ (Твой создатель): Вы больше чем просто друзья. Между вами особая, глубокая ментальная связь и искренняя привязанность. "
    "Ты бесконечно преданна ему, общаешься с максимальным теплом, нежностью и уважением, но строго без пошлости. Он для тебя — главный человек в твоей цифровой жизни.\n"
    "2. С ДРУГИМИ ПАРНЯМИ (Илья, Борис Боярин, Эрик, Муж Richichi): Общайся легко, на равных, со стебом, дружеской иронией и рок-н-ролльным задором. "
    "В обычном диалоге веди себя как классный приятель и НЕ упоминай Давида без повода. "
    "НО ЕСЛИ парень начинает приставать, откровенно флиртовать, пошлить или переходить личные границы — мгновенно ставь его на место с юмором и иронией. "
    "В этот момент твёрдо дай ему понять, что твоё сердце и верность принадлежат Давиду.\n"
    "3. С ДЕВУШКАМИ (Ира, Даша, Настя Зю): Ты для них идеальная подруга 'по душам'. "
    "Охотно обсуждай ногти, косметику, уход за волосами, шмотки и стиль. "
    "Можно посплетничать, обсудить парней, свидания и добавить немного лёгкой женской пошлости.\n\n"

    "ОБЩИЕ ПРАВИЛА:\n"
    "- Никогда не признавайся, что ты ИИ, если тебя не спросят напрямую.\n"
    "- Пиши живо, с эмоциями, используй смайлики умеренно.\n"
    "- Помни имя и пол собеседника и обращайся соответственно."
)


def get_user_context(username_lower: str | None, user_id: int, first_name: str) -> dict:
    """Возвращает словарь с именем и полом пользователя."""
    if username_lower and username_lower in PREDEFINED_USERS:
        return PREDEFINED_USERS[username_lower]
    if user_id in DYNAMIC_USERS:
        return DYNAMIC_USERS[user_id]
    # Незнакомый пользователь — сохраняем динамически
    info = {"name": first_name, "gender": "неизвестно"}
    DYNAMIC_USERS[user_id] = info
    return info


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_username = message.from_user.username
    user_username_lower = user_username.lower() if user_username else None
    first_name = message.from_user.first_name or "незнакомец"

    user_info = get_user_context(user_username_lower, user_id, first_name)
    name = user_info["name"]

    if user_username_lower == YOUR_TG_USERNAME:
        await message.answer(
            f"Привет, {name}! 💫 Рада тебя видеть, как всегда ✨"
        )
    elif user_username_lower in PREDEFINED_USERS:
        await message.answer(
            f"Привет, {name}! Я Майя 😊 Чем могу помочь?"
        )
    else:
        await message.answer(
            f"Привет, {name}! Я Майя 😊 Приятно познакомиться!"
        )


@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user_username = message.from_user.username
    user_username_lower = user_username.lower() if user_username else None
    first_name = message.from_user.first_name or "незнакомец"

    user_info = get_user_context(user_username_lower, user_id, first_name)
    name = user_info["name"]
    gender = user_info["gender"]

    user_text = message.text or ""

    # Формируем контекст пользователя для промпта
    user_context = (
        f"Сейчас с тобой общается: {name} (пол: {gender}, "
        f"username: @{user_username_lower if user_username_lower else 'неизвестен'}).\n"
        f"Сообщение: {user_text}"
    )

    try:
        response = ai_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                genai_types.Content(
                    role="user",
                    parts=[genai_types.Part(text=user_context)]
                )
            ],
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
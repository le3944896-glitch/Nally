import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)

TOKEN = "8353980401:AAHYZ7FX6eGb9-W2XS2nFUKCG1jDiSwC70s"
GEMINI_API_KEY = "AIzaSyBJijdP6gov1pFcx0hLJmxElYCdlg-vKvA"

bot = Bot(token=TOKEN)
dp = Dispatcher()

genai.configure(api_key=GEMINI_API_KEY)
# Используйте проверенную модель, если 2.5-flash-lite недоступна
model = genai.GenerativeModel("gemini-2.5-flash-lite")  # или "gemini-2.0-flash-exp"

SYSTEM_MESSAGE = """Вы - умный помощник. Тебя зовут Nally.
Отвечайте коротко, ясно и понятно.

Ответы форматируйте так:

😊 — улыбка, для дружелюбных ответов.

👍 — большой палец, для подтверждений.

❓ — вопрос, для запросов помощи.

✨ — искры, для креативных идей или магии ИИ.

🚀 — ракета, для быстрых результатов или инноваций.

🤖 — робот, основной символ ИИ и робота.

🔍 — поиск в интернете.

Используйте эмоджи для оформления."""

async def get_gemini_response(question: str) -> str:
    try:
        full_prompt = f"{SYSTEM_MESSAGE}\n\nВопрос: {question}"
        logging.info(f"Запрос к Gemini: {question[:50]}...")
        response = await asyncio.to_thread(model.generate_content, full_prompt)  # Асинхронно!
        logging.info("Ответ от Gemini получен")
        return response.text
    except Exception as e:
        logging.error(f"Ошибка Gemini: {e}")
        return f"❌ Ошибка: {str(e)}"

@dp.message(CommandStart())
async def cmd_start(message: Message):
    logging.info(f"/start от {message.from_user.id}")
    welcome_text = (
        "Перивет! Я Nally - твой помошник😉"
        "Просто пиши вопрос — я отвечу! 🚀"
    )
    await message.answer(welcome_text)

@dp.message(F.text)
async def handle_message(message: Message):
    logging.info(f"Сообщение от {message.from_user.id}: {message.text[:50]}")
    await bot.send_chat_action(message.chat.id, "typing")
    response = await get_gemini_response(message.text)

    if len(response) > 4090:
        # Разбиение на части
        parts = [p.strip() for p in response.split('\n\n') if p.strip()]
        current = ""
        for part in parts:
            if len(current) + len(part) + 2 > 4090:
                if current:
                    await message.answer(current)
                current = part
            else:
                current += ("\n\n" if current else "") + part
        if current:
            await message.answer(current)
    else:
        await message.answer(response)

async def main():
    logging.info("🤖 Бот запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

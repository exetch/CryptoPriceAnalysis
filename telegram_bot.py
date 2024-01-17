import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from dotenv import load_dotenv


load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

user_chat_ids = set()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    chat_id = message.chat.id
    if chat_id not in user_chat_ids:
        user_chat_ids.add(chat_id)
        await message.reply("Вы подписались на уведомления.")

async def send_notification(message: str):
    for chat_id in user_chat_ids:
        try:
            await bot.send_message(chat_id, message)
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")

async def run_bot():
    await dp.start_polling()



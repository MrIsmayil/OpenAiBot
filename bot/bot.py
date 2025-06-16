from aiogram import Bot, Dispatcher
from core.config import config
from handlers import common, prediction, chat, admin
import asyncio

async def main():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    
    # Подключаем роутеры
    dp.include_router(common.common_router)
    dp.include_router(prediction.prediction_router)
    dp.include_router(chat.chat_router)
    dp.include_router(admin.admin_router)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
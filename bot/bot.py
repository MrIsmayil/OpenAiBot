from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from core.config import config
from handlers import common, prediction, chat, admin
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    
    # Правильный порядок подключения роутеров (от более специфичных к общим)
    dp.include_router(admin.admin_router)
    dp.include_router(chat.chat_router)
    dp.include_router(prediction.prediction_router)
    dp.include_router(common.common_router)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
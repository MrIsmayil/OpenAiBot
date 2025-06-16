from aiogram import F, Router
from aiogram.types import Message
from core.keyboards import get_main_keyboard
from core.config import config

common_router = Router()

@common_router.message(F.text == "Старт")
async def cmd_start(message: Message):
    await message.answer(
        "Выберите действие:",
        reply_markup=get_main_keyboard(message.from_user.id in config.ADMIN_IDS)
    )

@common_router.message(F.text == "Выход")
async def cmd_exit(message: Message):
    await message.answer(
        "Выберите действие:",
        reply_markup=get_main_keyboard(message.from_user.id in config.ADMIN_IDS)
    )
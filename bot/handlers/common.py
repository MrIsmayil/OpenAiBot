from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command
from core.keyboards import get_main_keyboard
from core.config import config

common_router = Router()

@common_router.message(Command("start"))
@common_router.message(F.text.lower() == "старт")
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать! Я - умный бот. Выберите действие:",
        reply_markup=get_main_keyboard(message.from_user.id in config.ADMIN_IDS)
    )

@common_router.message(F.text == "Мой ID")
async def cmd_my_id(message: Message):
    await message.answer(f"Ваш ID: {message.from_user.id}")

@common_router.message(F.text == "Выход")
async def cmd_exit(message: Message):
    await message.answer(
        "Главное меню:",
        reply_markup=get_main_keyboard(message.from_user.id in config.ADMIN_IDS)
    )

@common_router.message()
async def handle_other_messages(message: Message):
    """Обработка всех остальных сообщений"""
    await message.answer(
        "Пожалуйста, выберите нужный режим из меню.",
        reply_markup=get_main_keyboard(message.from_user.id in config.ADMIN_IDS)
    )
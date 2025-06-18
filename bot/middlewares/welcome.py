from aiogram import BaseMiddleware
from aiogram.types import Message
from core.keyboards import get_start_keyboard

class WelcomeMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        # Для первого сообщения от пользователя (не /start и не "Старт")
        if not event.text or (event.text != "/start" and event.text.lower() != "старт"):
            await event.answer(
                "Добро пожаловать! Нажмите кнопку ниже:",
                reply_markup=get_start_keyboard()
            )
            return
        return await handler(event, data)
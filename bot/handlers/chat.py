from aiogram import F, Router
from aiogram.types import Message
from core.keyboards import get_chat_admin_keyboard, get_exit_keyboard
from models.chat_model import ChatModel

chat_router = Router()
chat_model = ChatModel()

@chat_router.message(F.text == "Болтать")
async def start_chat(message: Message):
    if message.from_user.id in config.ADMIN_IDS:
        await message.answer(
            "Выберите режим:",
            reply_markup=get_chat_admin_keyboard()
        )
    else:
        await message.answer(
            "Давайте пообщаемся! Напишите что-нибудь:",
            reply_markup=get_exit_keyboard()
        )
        # Устанавливаем состояние чата

@chat_router.message(F.text == "Обучать")
async def train_chat(message: Message):
    await message.answer(
        "Режим обучения. Введите запрос и ответ через '|':\nПример: Привет|Приветствую!",
        reply_markup=get_exit_keyboard()
    )

@chat_router.message()
async def process_chat(message: Message):
    if message.text == "Выход":
        return
    
    if "|" in message.text:
        # Обработка обучения
        query, response = message.text.split("|", 1)
        chat_model.add_example(query.strip(), response.strip())
        await message.answer("Пример добавлен!")
    else:
        # Обработка обычного сообщения
        response = chat_model.get_response(message.text)
        await message.answer(response)
        
        # Проверка на слова прощания
        if any(word in message.text.lower() for word in ["пока", "до свидания"]):
            await cmd_exit(message)
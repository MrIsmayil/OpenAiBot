from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from core.keyboards import get_chat_admin_keyboard, get_main_keyboard, get_exit_keyboard
from models.chat_model import ChatModel
from core.config import config
import logging

logger = logging.getLogger(__name__)
chat_router = Router()
chat_model = ChatModel()

class ChatStates(StatesGroup):
    chat_mode = State()
    add_question = State()
    add_answer = State()

@chat_router.message(F.text == "Болтать")
async def handle_chat_menu(message: Message, state: FSMContext):
    """Обработчик меню чата"""
    if message.from_user.id in config.ADMIN_IDS:
        await message.answer(
            "Меню общения:",
            reply_markup=get_chat_admin_keyboard()
        )
    else:
        await enter_chat_mode(message, state)

@chat_router.message(F.text == "Общение")
async def handle_chat_start(message: Message, state: FSMContext):
    """Обработчик входа в режим общения"""
    await enter_chat_mode(message, state)

async def enter_chat_mode(message: Message, state: FSMContext):
    """Функция входа в режим чата"""
    await state.set_state(ChatStates.chat_mode)
    await message.answer(
        "Режим общения активирован. Напишите ваше сообщение:",
        reply_markup=get_exit_keyboard()
    )

@chat_router.message(F.text == "Добавить (Чат)")
async def start_adding_chat_data(message: Message, state: FSMContext):
    """Начало добавления данных в чат"""
    await message.answer(
        "Введите фразу пользователя:",
        reply_markup=get_exit_keyboard()
    )
    await state.set_state(ChatStates.add_question)

@chat_router.message(ChatStates.add_question)
async def process_chat_question(message: Message, state: FSMContext):
    """Обработка вопроса для чата"""
    if message.text == "Выход":
        await state.clear()
        await message.answer(
            "Меню общения:",
            reply_markup=get_chat_admin_keyboard()
        )
        return

    await state.update_data(question=message.text.lower())
    await message.answer(
        "Теперь введите ответ бота:",
        reply_markup=get_exit_keyboard()
    )
    await state.set_state(ChatStates.add_answer)

@chat_router.message(ChatStates.add_answer)
async def process_chat_answer(message: Message, state: FSMContext):
    """Обработка ответа для чата"""
    if message.text == "Выход":
        await state.clear()
        await message.answer(
            "Меню общения:",
            reply_markup=get_chat_admin_keyboard()
        )
        return

    data = await state.get_data()
    if chat_model.add_example(data['question'], message.text):
        await message.answer("✅ Пример добавлен в чат!")
    else:
        await message.answer("⚠️ Такой пример уже существует")
    
    await state.clear()
    await message.answer(
        "Меню общения:",
        reply_markup=get_chat_admin_keyboard()
    )

@chat_router.message(F.text == "Обучать")
async def handle_train_chat(message: Message):
    """Обработчик обучения модели чата"""
    if chat_model.train():
        await message.answer(
            "✅ Модель чата успешно обучена!",
            reply_markup=get_chat_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Ошибка обучения модели чата!",
            reply_markup=get_chat_admin_keyboard()
        )

@chat_router.message(StateFilter(ChatStates.chat_mode), F.text == "Выход")
async def handle_exit_from_chat(message: Message, state: FSMContext):
    """Выход из режима чата"""
    await state.clear()
    await message.answer(
        "Режим общения завершен.",
        reply_markup=get_main_keyboard(message.from_user.id in config.ADMIN_IDS)
    )

@chat_router.message(StateFilter(ChatStates.chat_mode))
async def handle_chat_message(message: Message, state: FSMContext):
    """Обработка сообщений в режиме чата"""
    if message.text.lower() in ["пока", "до свидания"]:
        await handle_exit_from_chat(message, state)
        return
        
    response = chat_model.get_response(message.text)
    await message.answer(response)
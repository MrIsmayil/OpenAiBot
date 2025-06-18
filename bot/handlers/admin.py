from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from core.keyboards import get_main_keyboard, get_exit_keyboard
from models.ai_model import AIModel
from core.config import config
import logging

logger = logging.getLogger(__name__)
admin_router = Router()
ai_model = AIModel()

class AddDataStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_answer = State()

@admin_router.message(F.text == "Обучение")
async def train_model_handler(message: Message):
    """Обработчик обучения модели"""
    await message.answer("Начинаю обучение...")
    if ai_model.train():
        await message.answer("✅ Модель обучена и сохранена!")
    else:
        await message.answer("❌ Ошибка обучения. Проверьте данные.")

@admin_router.message(F.text == "Добавить")
async def add_data(message: Message, state: FSMContext):
    await message.answer(
        "Введите вопрос:",
        reply_markup=get_exit_keyboard()
    )
    await state.set_state(AddDataStates.waiting_for_question)

@admin_router.message(AddDataStates.waiting_for_question)
async def process_question(message: Message, state: FSMContext):
    if message.text == "Выход":
        await state.clear()
        await message.answer(
            "Главное меню:",
            reply_markup=get_main_keyboard(True)
        )
        return

    # Сохраняем оригинальный текст вопроса
    await state.update_data(question=message.text)
    await message.answer(
        "Теперь введите ответ:",
        reply_markup=get_exit_keyboard()
    )
    await state.set_state(AddDataStates.waiting_for_answer)

@admin_router.message(AddDataStates.waiting_for_answer)
async def process_answer(message: Message, state: FSMContext):
    if message.text == "Выход":
        await state.clear()
        await message.answer(
            "Главное меню:",
            reply_markup=get_main_keyboard(True)
        )
        return

    data = await state.get_data()
    ai_model.add_training_data(data['question'], message.text)
    await state.clear()
    await message.answer(
        "✅ Данные успешно добавлены!",
        reply_markup=get_main_keyboard(True)
    )

@admin_router.message(F.text == "Статус")
async def model_status_handler(message: Message):
    """Проверка статуса модели"""
    status = ai_model.get_status()
    data = ai_model.load_data()
    
    response = (
        f"📊 Статус модели:\n"
        f"• Обучена: {'Да' if status['is_trained'] else 'Нет'}\n"
        f"• Классов: {status['num_classes']}\n"
        f"• Примеров: {len(data['texts'])}\n"
        f"• Уникальных меток: {len(set(data['labels']))}\n"
        f"• Размер словаря: {status['vocab_size']}"
    )
    await message.answer(response)
from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from core.keyboards import get_exit_keyboard, get_main_keyboard
from models.ai_model import AIModel
from core.config import config
import logging

logger = logging.getLogger(__name__)
prediction_router = Router()
ai_model = AIModel()

class PredictionStates(StatesGroup):
    prediction_mode = State()

@prediction_router.message(F.text == "Спросить")
async def start_prediction_mode(message: Message, state: FSMContext):
    """Начало режима предсказаний"""
    if not ai_model.is_trained and not ai_model.load_model():
        await message.answer(
            "Модель не обучена. Админ должен обучить модель.",
            reply_markup=get_main_keyboard(message.from_user.id in config.ADMIN_IDS)
        )
        return
    
    await message.answer(
        "Режим вопрос-ответ активирован. Введите ваш вопрос:",
        reply_markup=get_exit_keyboard()
    )
    await state.set_state(PredictionStates.prediction_mode)

@prediction_router.message(F.text == "Выход", StateFilter(PredictionStates.prediction_mode))
async def exit_prediction_mode(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Режим вопрос-ответ завершен.",
        reply_markup=get_main_keyboard(message.from_user.id in config.ADMIN_IDS)
    )

@prediction_router.message(StateFilter(PredictionStates.prediction_mode))
async def process_prediction(message: Message):
    """Обработка текста для предсказания"""
    if message.text == "Выход":
        await message.answer(
            "Режим вопрос-ответ завершен.",
            reply_markup=get_main_keyboard(message.from_user.id in config.ADMIN_IDS)
        )
        return
    
    if not ai_model.is_trained:
        if not ai_model.load_model():
            await message.answer("Модель не обучена!")
            return
    
    try:
        response = ai_model.predict(message.text)
        await message.answer(response)
    except Exception as e:
        logger.error(f"Ошибка предсказания: {e}")
        await message.answer("Произошла ошибка при обработке запроса.")
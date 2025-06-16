from aiogram import F, Router
from aiogram.types import Message
from core.keyboards import get_exit_keyboard
from models.ai_model import AIModel

prediction_router = Router()
ai_model = AIModel()

@prediction_router.message(F.text == "Спросить")
async def start_prediction(message: Message):
    await message.answer(
        "Введите текст для предсказания:",
        reply_markup=get_exit_keyboard()
    )

@prediction_router.message()
async def process_prediction(message: Message):
    if message.text == "Выход":
        return
    
    prediction = ai_model.predict(message.text)
    await message.answer(f"🔮 Предсказание: {prediction}")
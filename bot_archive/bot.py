import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import config
from ai_model.model import AIModel

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Инициализация модели ИИ
ai_model = AIModel()

# Состояния для FSM
class TrainStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_label = State()

# Команда старт
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот с интеграцией ИИ.\n"
        "Доступные команды:\n"
        "/predict <текст> - предсказание на основе модели\n"
        "/train_model - обучить модель на текущих данных\n"
        "/add_data - добавить данные для обучения\n"
        "/model_status - статус модели\n"
        "/my_id - узнать свой ID"
    )

# Проверка свой ID
@dp.message(Command("my_id"))
async def cmd_my_id(message: types.Message):
    await message.answer(f"Ваш ID: {message.from_user.id}\n")
    
# Полная проверка свой ID
@dp.message(Command("my_id_full"))
async def cmd_my_id(message: types.Message):
    await message.answer(f"Ваш ID: {message.from_user.id}\n"
                       f"Администраторы: {config.ADMIN_IDS}")
    
#Debug logs
@dp.message(Command("debug_model"))
async def cmd_debug_model(message: types.Message):
    if message.from_user.id not in config.ADMIN_IDS:
        return
    
    status = ai_model.get_status()
    training_data = ai_model.get_training_data()
    
    response = (
        f"Статус модели:\n"
        f"Обучена: {status['is_trained']}\n"
        f"Классов: {status['num_classes']}\n"
        f"Слов в словаре: {status['vocab_size']}\n\n"
        f"Примеры данных:\n"
    )
    
    for text, label in zip(training_data['texts'][:5], training_data['labels'][:5]):
        response += f"- '{text}' → '{label}'\n"
    
    await message.answer(response)

# Проверка статуса модели
@dp.message(Command("model_status"))
async def cmd_model_status(message: types.Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("Эта команда доступна только администраторам.")
        return
    
    status = "обучена" if ai_model.is_trained else "не обучена"
    training_data = ai_model.get_training_data()
    await message.answer(
        f"Статус модели: {status}\n"
        f"Примеров для обучения: {len(training_data['texts'])}\n"
        f"Уникальных меток: {len(set(training_data.get('labels', [])))}"
    )

# Предсказание с помощью модели
@dp.message(Command("predict"))
async def cmd_predict(message: types.Message):
    text = message.text.split(maxsplit=1)
    if len(text) < 2:
        await message.answer("Формат: /predict ваш текст")
        return
    
    text = text[1].strip()
    if not text:
        await message.answer("Текст не может быть пустым")
        return
    
    try:
        prediction = ai_model.predict(text)
        await message.answer(f"🔮 Предсказание для '{text}':\n\n{prediction}")
    except Exception as e:
        logger.exception(f"Prediction failed for text: {text}")
        await message.answer("Произошла внутренняя ошибка при обработке запроса")

    

# Добавление данных для обучения
@dp.message(Command("add_data"))
async def cmd_add_data(message: types.Message, state: FSMContext):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("Эта команда доступна только администраторам.")
        return
    
    await state.set_state(TrainStates.waiting_for_text)
    await message.answer("Пришлите текст для добавления в обучающую выборку:")

@dp.message(TrainStates.waiting_for_text)
async def process_text(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(TrainStates.waiting_for_label)
    await message.answer("Теперь укажите метку для этого текста:")

@dp.message(TrainStates.waiting_for_label)
async def process_label(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = data['text']
    label = message.text
    
    ai_model.add_training_data(text, label)
    await message.answer(f"Добавлен текст с меткой '{label}' в обучающую выборку.")
    await state.clear()

# Обучение модели
@dp.message(Command("train_model"))
async def cmd_train_model(message: types.Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("Эта команда доступна только администраторам.")
        return
    
    training_data = ai_model.get_training_data()
    
    await message.answer("Начинаю обучение модели...")
    
    try:
        success = ai_model.train(training_data['texts'], training_data['labels'])
        if success:
            status = ai_model.get_status()
            await message.answer(
                "✅ Модель успешно обучена!\n"
                f"• Примеров: {len(training_data['texts'])}\n"
                f"• Классов: {status['num_classes']}\n"
                f"• Слов в словаре: {status['vocab_size']}"
            )
        else:
            await message.answer("❌ Ошибка при обучении модели. Добавьте больше разнообразных данных.")
    except Exception as e:
        logger.exception("Training failed")
        await message.answer(f"Ошибка: {str(e)}")




# @dp.message(Command("train_model"))
# async def cmd_train_model(message: types.Message):
#     if message.from_user.id not in config.ADMIN_IDS:
#         await message.answer("Эта команда доступна только администраторам.")
#         return
    
#     training_data = ai_model.get_training_data()
#     if len(training_data['texts']) < 10:
#         await message.answer(f"Недостаточно данных для обучения. Нужно минимум 10 примеров, сейчас {len(training_data['texts'])}.")
#         return
    
#     await message.answer("Начинаю обучение модели...")
    
#     try:
#         success = ai_model.train(training_data['texts'], training_data['labels'])
#         if success:
#             status = ai_model.get_status()
#             await message.answer(
#                 f"Модель успешно обучена!\n"
#                 f"Классов: {status['num_classes']}\n"
#                 f"Размер словаря: {status['vocab_size']}"
#             )
#         else:
#             await message.answer("Ошибка при обучении модели. Проверьте логи.")
#     except Exception as e:
#         logger.exception("Training failed")
#         await message.answer(f"Критическая ошибка при обучении: {e}")



# Обработка любого текста (можно использовать для чата с ИИ)
@dp.message(F.text)
async def handle_text(message: types.Message):
    if not ai_model.is_trained:
        await message.answer("Модель не обучена. Сначала обучите модель.")
        return
    
    # Просто демонстрация - в реальном боте можно подключить более сложную логику
    prediction = ai_model.predict(message.text)
    await message.answer(f"Я думаю, это относится к категории: {prediction}")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
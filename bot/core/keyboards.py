from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_start_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Старт")]],
        resize_keyboard=True
    )

def get_main_keyboard(is_admin: bool = False):
    buttons = [
        [KeyboardButton(text="Спросить")],
        [KeyboardButton(text="Болтать")],
        [KeyboardButton(text="Мой ID")]
    ]
    if is_admin:
        buttons.extend([
            [KeyboardButton(text="Обучение")],
            [KeyboardButton(text="Добавить")],
            [KeyboardButton(text="Статус")]
        ])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_exit_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Выход")]],
        resize_keyboard=True
    )

def get_chat_admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Болтать"), KeyboardButton(text="Обучать")],
            [KeyboardButton(text="Выход")]
        ],
        resize_keyboard=True
    )
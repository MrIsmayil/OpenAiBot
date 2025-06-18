import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Токен бота и ID администраторов
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_IDS = [int(id_) for id_ in os.getenv("ADMIN_IDS", "").split(",") if id_]
    
    # Пути к файлам и директориям
    BASE_DIR = Path(__file__).parent.parent
    MODEL_PATH = str(BASE_DIR / "ai_model" / "saved_model")
    TRAINING_DATA_PATH = str(BASE_DIR / "data" / "training_data.json")
    CHAT_DATA_PATH = str(BASE_DIR / "data" / "chat_data.json")
    
    # Создаем директории, если они не существуют
    os.makedirs(MODEL_PATH, exist_ok=True)
    os.makedirs(os.path.dirname(TRAINING_DATA_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(CHAT_DATA_PATH), exist_ok=True)

config = Config()
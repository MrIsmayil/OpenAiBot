import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    # ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(',')))
    ADMIN_IDS = [int(id_.strip()) for id_ in os.getenv('ADMIN_IDS', '').split(',') if id_.strip()]
    # ADMIN_IDS = [7713136125]

    
    # Настройки модели ИИ
    MODEL_PATH = 'ai_model/saved_model'
    TRAINING_DATA_PATH = 'data/training_data.json'
    
config = Config()
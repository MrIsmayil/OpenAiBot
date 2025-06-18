import json
import logging
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import joblib
from core.config import config

logger = logging.getLogger(__name__)

class ChatModel:
    def __init__(self):
        self.data_path = Path(config.CHAT_DATA_PATH)
        self.model_path = Path(config.MODEL_PATH) / "chat_model.joblib"
        self.vectorizer = TfidfVectorizer()
        self.nn_model = NearestNeighbors(n_neighbors=1)
        self.examples = {}
        self._init_data_file()
        self.load_data()

    def _init_data_file(self):
        """Инициализация файла данных"""
        if not self.data_path.exists():
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            logger.info(f"Создан новый файл чата: {self.data_path}")

    def load_data(self):
        """Загрузка данных чата"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.examples = json.load(f)
            
            if self.model_path.exists():
                model_data = joblib.load(self.model_path)
                self.vectorizer = model_data['vectorizer']
                self.nn_model = model_data['nn_model']
        except Exception as e:
            logger.error(f"Ошибка загрузки чата: {e}")
            self.examples = {}

    def save_model(self):
        """Сохранение модели чата"""
        model_data = {
            'vectorizer': self.vectorizer,
            'nn_model': self.nn_model
        }
        joblib.dump(model_data, self.model_path)

    def train(self):
        """Обучение модели чата"""
        try:
            if not self.examples:
                raise ValueError("Нет данных для обучения")
                
            questions = list(self.examples.keys())
            X = self.vectorizer.fit_transform(questions)
            self.nn_model.fit(X)
            self.save_model()
            return True
        except Exception as e:
            logger.error(f"Ошибка обучения чата: {e}")
            return False

    def add_example(self, question: str, answer: str) -> bool:
        """Добавление нового примера"""
        question = question.lower().strip()
        if not question or not answer:
            return False
            
        if question not in self.examples:
            self.examples[question] = answer
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(self.examples, f, ensure_ascii=False, indent=2)
            return True
        return False

    def get_response(self, query: str) -> str:
        """Получение ответа на сообщение"""
        try:
            query = query.lower().strip()
            
            # Точное совпадение
            if query in self.examples:
                return self.examples[query]
            
            # Поиск похожих вопросов
            if self.model_path.exists():
                X_query = self.vectorizer.transform([query])
                distances, indices = self.nn_model.kneighbors(X_query)
                if distances[0][0] < 0.8:  # Порог схожести
                    closest_q = list(self.examples.keys())[indices[0][0]]
                    return self.examples[closest_q]
        except Exception as e:
            logger.error(f"Ошибка поиска ответа: {e}")
        
        return "Я вас не понял. Можете переформулировать?"
import os
import json
import logging
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import joblib
from core.config import config

logger = logging.getLogger(__name__)

class AIModel:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(lowercase=True)  # Добавляем lowercase=True
        self.classifier = RandomForestClassifier()
        self.label_to_index = {}
        self.index_to_label = {}
        self.is_trained = False
        self.original_texts = []  # Сохраняем оригинальные тексты для точного совпадения
        
        os.makedirs(config.MODEL_PATH, exist_ok=True)
        os.makedirs(os.path.dirname(config.TRAINING_DATA_PATH), exist_ok=True)
        self.load_data()

    def load_data(self):
        """Загружает данные из файла, сохраняя оригинальные тексты"""
        try:
            if os.path.exists(config.TRAINING_DATA_PATH):
                with open(config.TRAINING_DATA_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if not isinstance(data, dict) or 'texts' not in data or 'labels' not in data:
                        raise ValueError("Invalid data format")
                    # Сохраняем оригинальные тексты и их нижний регистр
                    self.original_texts = data['texts']
                    self.lower_texts = [text.lower() for text in data['texts']]
                    return {"texts": self.lower_texts, "labels": data['labels']}
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
    
        self.original_texts = []
        self.lower_texts = []
        return {"texts": [], "labels": []}

    def predict(self, text: str) -> str:
        """Предсказывает метку для текста (нечувствителен к регистру)"""
        if not self.is_trained:
            raise ValueError("Модель не обучена")
        
        try:
            text_lower = text.lower()
            data = self.load_data()
            
            # Проверка точного совпадения (без учета регистра)
            for i, lower_text in enumerate(self.lower_texts):
                if text_lower == lower_text:
                    return data['labels'][i]
            
            # Если нет точного совпадения - используем модель
            X = self.vectorizer.transform([text_lower])
            predicted_idx = self.classifier.predict(X)[0]
            return self.index_to_label.get(predicted_idx, "Извините, я не знаю ответа на этот вопрос.")
        except Exception as e:
            logger.error(f"Ошибка предсказания: {e}")
            return "Произошла ошибка при обработке запроса."

    def load_model(self):
        """Загружает модель с диска"""
        try:
            if os.path.exists(f"{config.MODEL_PATH}/model.joblib"):
                model_data = joblib.load(f"{config.MODEL_PATH}/model.joblib")
                self.vectorizer = model_data['vectorizer']
                self.classifier = model_data['classifier']
                self.label_to_index = model_data['label_to_index']
                self.index_to_label = model_data['index_to_label']
                self.is_trained = True
                logger.info("Модель успешно загружена")
                return True
        except Exception as e:
            logger.error(f"Ошибка загрузки модели: {e}")
        return False

    def save_data(self, data):
        """Сохраняет данные в файл"""
        try:
            with open(config.TRAINING_DATA_PATH, 'w', encoding='utf-8') as f:
                # Сохраняем оригинальные тексты
                json.dump({"texts": self.original_texts, "labels": data['labels']}, 
                          f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения данных: {e}")

    def add_training_data(self, text: str, label: str):
        """Добавляет новые данные для обучения"""
        text_lower = text.lower()
        data = self.load_data()
        
        # Проверяем на дубликаты (без учета регистра)
        if text_lower in self.lower_texts:
            return False
            
        self.original_texts.append(text)
        self.lower_texts.append(text_lower)
        data['texts'].append(text_lower)
        data['labels'].append(label)
        
        try:
            with open(config.TRAINING_DATA_PATH, 'w', encoding='utf-8') as f:
                json.dump({"texts": self.original_texts, "labels": data['labels']}, 
                        f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения данных: {e}")
            return False

    def train(self):
        """Обучает модель"""
        try:
            data = self.load_data()
            texts = data['texts']
            labels = data['labels']
            
            if len(texts) < 10:
                raise ValueError("Нужно минимум 10 примеров")
            if len(set(labels)) < 2:
                raise ValueError("Нужно минимум 2 разных метки")
            
            self.label_to_index = {label: idx for idx, label in enumerate(set(labels))}
            self.index_to_label = {idx: label for label, idx in self.label_to_index.items()}
            
            y = [self.label_to_index[label] for label in labels]
            X = self.vectorizer.fit_transform(texts)
            self.classifier.fit(X, y)
            self.is_trained = True
            
            self.save_model()
            return True
        except Exception as e:
            logger.error(f"Ошибка обучения: {e}")
            return False

    def save_model(self):
        """Сохраняет модель на диск"""
        model_data = {
            'vectorizer': self.vectorizer,
            'classifier': self.classifier,
            'label_to_index': self.label_to_index,
            'index_to_label': self.index_to_label
        }
        joblib.dump(model_data, f"{config.MODEL_PATH}/model.joblib")

    def get_status(self):
        """Возвращает статус модели"""
        data = self.load_data()
        vocab_size = len(self.vectorizer.vocabulary_) if hasattr(self.vectorizer, 'vocabulary_') else 0
        
        return {
            'is_trained': self.is_trained,
            'num_classes': len(self.label_to_index),
            'vocab_size': vocab_size,
            'examples_count': len(data['texts'])
        }
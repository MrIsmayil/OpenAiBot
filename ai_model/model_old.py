import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import json
import os
from pathlib import Path
from config import config

class AIModel:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.classifier = MultinomialNB()
        self.labels = []
        self.is_trained = False
        
        if os.path.exists(config.MODEL_PATH):
            self.load_model()
    
    def preprocess_data(self, texts, labels=None):
        if not self.is_trained and labels is not None:
            # Сохраняем уникальные метки
            self.labels = sorted(list(set(labels)))
            # Преобразуем метки в числовые индексы
            label_to_index = {label: idx for idx, label in enumerate(self.labels)}
            y = [label_to_index[label] for label in labels]
            
            X = self.vectorizer.fit_transform(texts)
            self.classifier.fit(X, y)
            self.is_trained = True
            self.save_model()
        elif self.is_trained:
            X = self.vectorizer.transform(texts)
            return X
        return None
    
    def predict(self, text):
        if not self.is_trained:
            return "Модель не обучена. Пожалуйста, обучите модель сначала."
        
        try:
            X = self.vectorizer.transform([text])
            pred = self.classifier.predict(X)
            return self.labels[int(pred[0])]
        except Exception as e:
            print(f"Ошибка предсказания: {e}")
            return "Ошибка при обработке запроса"
    
    
    def train(self, texts, labels):
        self.preprocess_data(texts, labels)
        self.is_trained = True
        self.save_model()
    
    def save_model(self):
        import joblib
        Path(config.MODEL_PATH).mkdir(parents=True, exist_ok=True)
        joblib.dump({
            'vectorizer': self.vectorizer,
            'classifier': self.classifier,
            'labels': self.labels
        }, f"{config.MODEL_PATH}/model.joblib")
    
    def load_model(self):
        import joblib
        try:
            model_data = joblib.load(f"{config.MODEL_PATH}/model.joblib")
            self.vectorizer = model_data['vectorizer']
            self.classifier = model_data['classifier']
            self.labels = model_data['labels']
            self.is_trained = True
        except Exception as e:
            print(f"Ошибка загрузки модели: {e}")
            self.is_trained = False
    
    def get_training_data(self):
        try:
            with open(config.TRAINING_DATA_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"texts": [], "labels": []}
    
    def add_training_data(self, text, label):
        data = self.get_training_data()
        data['texts'].append(text)
        data['labels'].append(label)
        
        with open(config.TRAINING_DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    
    def debug_model(self):
        print("Текущие метки:", self.labels)
        print("Размер словаря:", len(self.vectorizer.vocabulary_))
        if hasattr(self.classifier, 'classes_'):
            print("Классы классификатора:", self.classifier.classes_)
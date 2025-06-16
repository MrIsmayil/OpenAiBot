import numpy as np
import os
import json

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
from config import config
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class AIModel:
    def __init__(self):
        # self.vectorizer = TfidfVectorizer(
        #     min_df=2,
        #     max_df=0.9,
        #     ngram_range=(1, 2),
        #     stop_words=['это', 'все', 'такие']
        # )
        self.vectorizer = TfidfVectorizer(
            min_df=1,  # Учитываем слова, встречающиеся хотя бы 1 раз
            max_df=0.95,  # Игнорируем очень частые слова (95% документов)
            ngram_range=(1, 3),  # Учитываем словосочетания до 3 слов
            stop_words=['это', 'все', 'такие', 'тоже', 'очень'],  # Дополнительные стоп-слова
            analyzer='word'  # Анализируем по словам
        )
        # self.classifier = RandomForestClassifier(
        #     n_estimators=100,
        #     class_weight='balanced'
        # )
        self.classifier = RandomForestClassifier(
            n_estimators=200,  # Увеличиваем количество деревьев
            class_weight='balanced',
            max_depth=10  # Ограничиваем глубину деревьев
        )
        self.label_to_index = {}
        self.index_to_label = {}
        self.is_trained = False
        
        if os.path.exists(f"{config.MODEL_PATH}/model.joblib"):
            self.load_model()
    
    def train(self, texts, labels):
        try:
            # Проверяем, что у нас достаточно данных
            unique_labels = list(set(labels))
            if len(unique_labels) < 2:
                raise ValueError("Нужно как минимум 2 разных класса для обучения")
                
            if len(texts) < 20:
                raise ValueError("Нужно как минимум 20 примеров для обучения")
            
            # Создаем маппинг меток
            self.label_to_index = {label: idx for idx, label in enumerate(unique_labels)}
            self.index_to_label = {idx: label for label, idx in self.label_to_index.items()}
            
            # Преобразуем метки
            y = np.array([self.label_to_index[label] for label in labels])
            
            # Векторизуем и обучаем
            X = self.vectorizer.fit_transform(texts)
            self.classifier.fit(X, y)
            self.is_trained = True
            
            self.save_model()
            logger.info(f"Model trained with {len(texts)} samples, {len(unique_labels)} classes")
            return True
        except Exception as e:
            logger.error(f"Training error: {e}")
            return False
    
    def predict(self, text):
        if not self.is_trained:
            return "Модель не обучена"
        
        try:
            X = self.vectorizer.transform([text])

            logger.info(f"X: {X}")
            # print("X", X)
            
            # Проверка на неизвестные слова
            # if X.sum() == 0:
            # return "Не могу определить (неизвестные слова)"

            # Попробуем разбить текст на отдельные слова
            words = text.split()
            known_words = [w for w in words if w in self.vectorizer.vocabulary_]
            logger.info(f"words: {words}")
            logger.info(f"known_words: {known_words}")
            # print('words', words)
            # print('known_words', known_words)
            if not known_words:
                return "Не могу определить (неизвестные слова)"
            
            # Собираем новый текст только из известных слов
            new_text = ' '.join(known_words)
            X = self.vectorizer.transform([new_text])
            logger.info(f"X2: {X}")
            # print('X2', X)
            if X.sum() == 0:
                return "Не могу определить (неизвестные слова)"
                
            prediction = self.classifier.predict(X)[0]
            return self.index_to_label[prediction]
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return "Ошибка обработки"
    
    def save_model(self):
        Path(config.MODEL_PATH).mkdir(parents=True, exist_ok=True)
        model_data = {
            'vectorizer': self.vectorizer,
            'classifier': self.classifier,
            'label_to_index': self.label_to_index,
            'index_to_label': self.index_to_label
        }
        joblib.dump(model_data, f"{config.MODEL_PATH}/model.joblib")
    
    def load_model(self):
        try:
            model_data = joblib.load(f"{config.MODEL_PATH}/model.joblib")
            self.vectorizer = model_data['vectorizer']
            self.classifier = model_data['classifier']
            self.label_to_index = model_data['label_to_index']
            self.index_to_label = model_data['index_to_label']
            self.is_trained = True
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Load model error: {e}")
            self.is_trained = False
    
    def get_status(self):
        return {
            'is_trained': self.is_trained,
            'num_classes': len(self.label_to_index),
            'vocab_size': len(self.vectorizer.vocabulary_) if hasattr(self.vectorizer, 'vocabulary_') else 0
        }
    
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















# import numpy as np
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.naive_bayes import MultinomialNB
# import json
# import os
# from pathlib import Path
# import joblib
# from config import config
# import logging

# from sklearn.linear_model import LogisticRegression
# from sklearn.calibration import CalibratedClassifierCV

# logger = logging.getLogger(__name__)

# class AIModel:
#     def __init__(self):
#         self.vectorizer = TfidfVectorizer()
#         self.classifier = MultinomialNB()
#         self.label_to_index = {}
#         self.index_to_label = {}
#         self.is_trained = False

#         self.vectorizer = TfidfVectorizer(min_df=2, max_df=0.8)  # Игнорируем редкие и частые слова
#         self.classifier = CalibratedClassifierCV(LogisticRegression(max_iter=1000))
        
#         if os.path.exists(f"{config.MODEL_PATH}/model.joblib"):
#             self.load_model()
    
#     def train(self, texts, labels):
#         try:
#             # Очищаем предыдущую модель
#             # self.vectorizer = TfidfVectorizer()
#             # self.classifier = MultinomialNB()

#             self.vectorizer = TfidfVectorizer(
#                 min_df=2, 
#                 max_df=0.8,
#                 ngram_range=(1, 2)  # Учитываем словосочетания
#             )
#             self.classifier = CalibratedClassifierCV(
#                 LogisticRegression(
#                     max_iter=1000,
#                     class_weight='balanced'  # Балансировка классов
#                 )
#             )
            
#             # Создаем маппинг меток
#             unique_labels = sorted(list(set(labels)))
#             self.label_to_index = {label: idx for idx, label in enumerate(unique_labels)}
#             self.index_to_label = {idx: label for label, idx in self.label_to_index.items()}
            
#             # Преобразуем метки в индексы
#             y = [self.label_to_index[label] for label in labels]
            
#             # Векторизуем и обучаем
#             X = self.vectorizer.fit_transform(texts)
#             self.classifier.fit(X, y)
#             self.is_trained = True
            
#             self.save_model()
#             logger.info(f"Model trained with {len(texts)} samples, {len(unique_labels)} classes")
#             return True
#         except Exception as e:
#             logger.error(f"Training error: {e}")
#             return False
    
#     def predict(self, text):
#         if not self.is_trained:
#             return "Модель не обучена"
        
#         try:
#             # X = self.vectorizer.transform([text])
#             # pred_idx = self.classifier.predict(X)[0]
#             # return self.index_to_label[pred_idx]

#             X = self.vectorizer.transform([text])
        
#             # Проверяем, есть ли известные слова в запросе
#             if X.sum() == 0:
#                 return "Не могу определить (неизвестные слова)"
            
#             pred_proba = self.classifier.predict_proba(X)[0]
#             max_prob = pred_proba.max()
            
#             # Если вероятность низкая - считаем неизвестным
#             if max_prob < 0.6:  # Порог можно настроить
#                 return "Не могу точно определить"
                
#             pred_idx = pred_proba.argmax()
#             return self.index_to_label[pred_idx]
#         except Exception as e:
#             logger.error(f"Prediction error for text '{text}': {e}")
#             return f"Ошибка: {str(e)}"
    
#     def save_model(self):
#         Path(config.MODEL_PATH).mkdir(parents=True, exist_ok=True)
#         model_data = {
#             'vectorizer': self.vectorizer,
#             'classifier': self.classifier,
#             'label_to_index': self.label_to_index,
#             'index_to_label': self.index_to_label
#         }
#         joblib.dump(model_data, f"{config.MODEL_PATH}/model.joblib")
    
#     def load_model(self):
#         try:
#             model_data = joblib.load(f"{config.MODEL_PATH}/model.joblib")
#             self.vectorizer = model_data['vectorizer']
#             self.classifier = model_data['classifier']
#             self.label_to_index = model_data['label_to_index']
#             self.index_to_label = model_data['index_to_label']
#             self.is_trained = True
#             logger.info("Model loaded successfully")
#         except Exception as e:
#             logger.error(f"Load model error: {e}")
#             self.is_trained = False
    
#     def get_status(self):
#         return {
#             'is_trained': self.is_trained,
#             'num_classes': len(self.label_to_index),
#             'vocab_size': len(self.vectorizer.vocabulary_) if hasattr(self.vectorizer, 'vocabulary_') else 0
#         }
    
#     def get_training_data(self):
#         try:
#             with open(config.TRAINING_DATA_PATH, 'r', encoding='utf-8') as f:
#                 return json.load(f)
#         except (FileNotFoundError, json.JSONDecodeError):
#             return {"texts": [], "labels": []}
    
#     def add_training_data(self, text, label):
#         data = self.get_training_data()
#         data['texts'].append(text)
#         data['labels'].append(label)
        
#         with open(config.TRAINING_DATA_PATH, 'w', encoding='utf-8') as f:
#             json.dump(data, f, ensure_ascii=False, indent=2)

    
#     def debug_model(self):
#         print("Текущие метки:", self.labels)
#         print("Размер словаря:", len(self.vectorizer.vocabulary_))
#         if hasattr(self.classifier, 'classes_'):
#             print("Классы классификатора:", self.classifier.classes_)
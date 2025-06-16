import json
from pathlib import Path
from typing import Dict, List

class ChatModel:
    def __init__(self):
        self.data_path = Path("data/chat_data.json")
        self.examples: Dict[str, List[str]] = {}
        self.load_data()

    def load_data(self):
        if self.data_path.exists():
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.examples = json.load(f)

    def save_data(self):
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(self.examples, f, ensure_ascii=False, indent=2)

    def add_example(self, query: str, response: str):
        if query not in self.examples:
            self.examples[query] = []
        self.examples[query].append(response)
        self.save_data()

    def get_response(self, query: str) -> str:
        for key in self.examples:
            if key.lower() in query.lower():
                return self.examples[key][0]  # Возвращаем первый вариант
        return "Я не знаю, что ответить. Научите меня!"
import json
import random

class n8_model():
    sentences: list[str]
    mistakes: list[str]
    answers: list[int]

    def __init__(self, data: dict):
        self.sentences = [sentence.replace("\u202f", " ") for sentence in data["sentences"]]
        self.mistakes = [mistake.replace("\u202f", " ") for mistake in data["mistakes"]]
        self.answers = data['answers']

class n8_loader():
    models: list[n8_model] = []

    def load_file(self, file_name: str) -> None:
        path = f'res\\n8\\{file_name}'
        with open(path, encoding='utf-8') as file:
            data = json.load(file)
            for d in data:
                nm = n8_model(d)
                self.models.append(nm)

    def get_random_model(self) -> n8_model:
        ri = random.randint(0, len(self.models) - 1)
        return self.models[ri]

syntactic_norms_and_rules = n8_loader()
syntactic_norms_and_rules.load_file('n8.json')
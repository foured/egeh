import random

class number4_loader():
    def load_file(self, file_name: str):
        path = f'res\\n4\\{file_name}'
        with open(path, encoding='utf-8') as file:
            words = [word.split() for word in [l.strip() for l in file]]
            self.c_words = [word[0] for word in words]
            self.w_words = [word[1] for word in words]

    def get_random_pair(self) -> tuple[str, str]:
        ri = random.randint(0, len(self.c_words) - 1)
        return self.c_words[ri], self.w_words[ri]
    
    def is_word_correct(self, word: str) -> bool:
        return word in self.c_words
    
    def get_correct_words_as_str(self) -> str:
        ret = ''
        for w in self.c_words:
            ret += '\n' + w
        return ret


orthoepy = number4_loader()
orthoepy.load_file('n4_2024.txt')

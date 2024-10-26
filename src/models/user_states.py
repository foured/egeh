from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from src.keyboards import reply
from abc import abstractmethod

import random
import enum

class BaseUserState():
    name: str
    tree: 'StatesTree'

    def __init__(self, name: str, tree: 'StatesTree'):
        self.name = name
        self.tree = tree

    @abstractmethod
    async def process_message(self, message: Message):
        pass

    @abstractmethod
    async def enable(self):
        pass
    
    @abstractmethod
    async def disable(self):
        pass

class StatesTree():
    states: list[BaseUserState] = []
    current_state: int = 0
    id: str
    user: 'User'

    def __init__(self, id: str, user: 'User'):
        self.user = user
        self.id = id

    def add_state(self, s: BaseUserState) -> None:
        self.states.append(s)

    async def set_state_by_name(self, name: str) -> None:
        for i in range(0, len(self.states)):
            if self.states[i].name == name:
                await self.states[self.current_state].disable()
                self.current_state = i
                await self.states[self.current_state].enable()
                return
            
        raise ValueError(f"No such state in tree with name: {name}.") 
    
    async def execute_current_state(self, message: Message):
        await self.states[self.current_state].process_message(message)

class SubState(enum.Enum):
        MENU = 0
        GAME = 1
        RESTART = 2

class MainMenuState(BaseUserState):
    def __init__(self, tree: StatesTree):
        super().__init__('main_menu', tree)

    async def process_message(self, message: Message):
        txt = message.text
        if txt == 'Номер 4':
            await self.tree.set_state_by_name('orthoepy')
        elif txt == 'Номер 8':
            await self.tree.set_state_by_name('syntactic_norms_and_rules')
        else:
            await self.tree.user.bot.send_message(
                chat_id=self.tree.id, 
                text='Нажмите на клавиатуру!',
                reply_markup=reply.main_menu_kb) 

    async def enable(self):
        await self.tree.user.bot.send_message(
            chat_id=self.tree.id, 
            text='Вы в главном меню. Выберите функцию.',
            reply_markup=reply.main_menu_kb)
    
    async def disable(self):
        ...

class OrthoepyState(BaseUserState):
    sub_state : SubState = SubState.MENU
    count: int = 0

    def __init__(self, tree: StatesTree):
        super().__init__('orthoepy', tree)

    def generate_keyboard(self) -> ReplyKeyboardMarkup:
        from src.logic.number4 import orthoepy
        lp = list(orthoepy.get_random_pair())
        random.shuffle(lp)
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=lp[0]),
                KeyboardButton(text=lp[1])]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        return kb

    async def process_message(self, message: Message):
        txt = message.text
        from src.logic.number4 import orthoepy

        if self.sub_state == SubState.GAME:
            if orthoepy.is_word_correct(txt):
                self.count += 1
                await message.answer('✅Правльно!', reply_markup=self.generate_keyboard())
            else:
                if self.count > self.tree.user.data.orthoepy_record:
                    self.tree.user.data.orthoepy_record = self.count
                    await message.answer(f'❌Ошибка! 🎉Новый рекорд: {self.count}', reply_markup=reply.restart_back_kb)
                else:
                    await message.answer(f'❌Ошибка! Счёт: {self.count}', reply_markup=reply.restart_back_kb)
                self.sub_state = SubState.RESTART
            
        elif self.sub_state == SubState.RESTART:
            if txt.lower() == 'заново':
                await self.start_game()
            elif txt.lower() == 'назад':
                await self.enable()
            else:
                await self.tree.user.bot.send_message(
                        chat_id=self.tree.id, 
                        text='Нажмите на клавиатуру!', 
                        reply_markup=reply.restart_back_kb)
                
        elif self.sub_state == SubState.MENU:
            if txt.lower() == 'начать':
                await self.start_game()
            elif txt.lower() == 'рекорд':
                await self.tree.user.bot.send_message(
                        chat_id=self.tree.id, 
                        text=f'Рекорд: {self.tree.user.data.orthoepy_record}', 
                        reply_markup=reply.orthoepy_menu_kb)
            elif txt.lower() == 'все слова':
                await self.tree.user.bot.send_message(
                        chat_id=self.tree.id, 
                        text=f'Вот все слова: {orthoepy.get_correct_words_as_str()}', 
                        reply_markup=reply.orthoepy_menu_kb)
            elif txt.lower() == 'назад':
                await self.tree.set_state_by_name('main_menu')
            else:
                await self.tree.user.bot.send_message(
                        chat_id=self.tree.id, 
                        text='Нажмите на клавиатуру!', 
                        reply_markup=reply.orthoepy_menu_kb)

    async def start_game(self):
        self.sub_state = SubState.GAME
        self.count = 0
        await self.tree.user.bot.send_message(
            chat_id=self.tree.id, 
            text='Выберите слово с правильным ударением.', 
            reply_markup=self.generate_keyboard())

    async def enable(self):
        self.sub_state = SubState.MENU
        await self.tree.user.bot.send_message(
            chat_id=self.tree.id, 
            text='Орфоэпия меню.', 
            reply_markup=reply.orthoepy_menu_kb)
    
    async def disable(self):
        ...

class SyntacticNormsAndRules(BaseUserState):
    sub_state: SubState = SubState.MENU
    count: int = 0

    from src.logic.number8 import syntactic_norms_and_rules
    class TaskHandler():
        from src.logic.number8 import n8_model

        current_model: n8_model = None
        current_idx: int = 0

        def gen_new(self) -> str:
            from src.logic.number8 import syntactic_norms_and_rules
            
            self.current_model = syntactic_norms_and_rules.get_random_model()
            self.current_idx = random.randint(0, len(self.current_model.sentences) - 1)
            return self.current_model.sentences[self.current_idx]
        
        def check(self, answer: str) -> bool:
            for i in range(0, len(self.current_model.mistakes)):
                m = self.current_model.mistakes[i]
                if m.lower() == answer:
                    return i == self.current_idx
            return False
        
        def get_right(self) -> str:
            return self.current_model.mistakes[self.current_idx]

    task_handler: TaskHandler = TaskHandler()

    def __init__(self, tree: StatesTree):
        super().__init__('syntactic_norms_and_rules', tree)

    async def process_message(self, message: Message):
        txt = message.text
        if self.sub_state == SubState.MENU:
            if txt.lower() == 'начать':
                await self.start_game()
            elif txt.lower() == 'рекорд':
                await self.tree.user.bot.send_message(
                        chat_id=self.tree.id, 
                        text=f'Рекорд: {self.tree.user.data.syntactic_norms_and_rules_record}', 
                        reply_markup=reply.syntactic_norms_and_rules_menu_kb)
            elif txt.lower() == 'назад':
                await self.tree.set_state_by_name('main_menu')
            else:
                await self.tree.user.bot.send_message(
                        chat_id=self.tree.id, 
                        text='Нажмите на клавиатуру!', 
                        reply_markup=reply.syntactic_norms_and_rules_menu_kb)
        elif self.sub_state == SubState.RESTART:
            if txt.lower() == 'заново':
                await self.start_game()
            elif txt.lower() == 'назад':
                await self.enable()
            else:
                await self.tree.user.bot.send_message(
                        chat_id=self.tree.id, 
                        text='Нажмите на клавиатуру!', 
                        reply_markup=reply.restart_back_kb)
        elif self.sub_state == SubState.GAME:
            if self.task_handler.check(txt.lower()):
                self.count += 1
                await message.answer('✅Правльно!')
                await self.game_tick()
            else:
                self.sub_state = SubState.RESTART
                if self.count > self.tree.user.data.syntactic_norms_and_rules_record:
                    self.tree.user.data.syntactic_norms_and_rules_record = self.count
                    await message.answer(f'❌Ошибка! 🎉Новый рекорд: {self.count}!\n' 
                                         f'правильный ответ: {self.task_handler.get_right()}',
                                         reply_markup=reply.restart_back_kb)
                else:
                    await message.answer(f'❌Ошибка! Счёт: {self.count}!\n' 
                                         f'правильный ответ: {self.task_handler.get_right()}',
                                         reply_markup=reply.restart_back_kb)


    async def start_game(self):
        self.sub_state = SubState.GAME
        self.count = 0
        await self.tree.user.bot.send_message(
            chat_id=self.tree.id, 
            text='Выбериете какая ошибка встречается в предложении.')
        await self.game_tick()

    async def game_tick(self):
        await self.tree.user.bot.send_message(
            chat_id=self.tree.id, 
            text=self.task_handler.gen_new(),
            reply_markup=self.generate_keyboard())

    def generate_keyboard(self) -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        l = self.task_handler.current_model.mistakes.copy()
        random.shuffle(l)
        [builder.button(text=item) for item in l]
        builder.adjust(*[1] * len(self.task_handler.current_model.mistakes))
        return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

    async def enable(self):
        self.sub_state = SubState.MENU
        await self.tree.user.bot.send_message(
            chat_id=self.tree.id, 
            text='Синтаксические нормы и правила меню.', 
            reply_markup=reply.syntactic_norms_and_rules_menu_kb)
    
    async def disable(self):
        pass

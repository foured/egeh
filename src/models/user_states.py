from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from src.keyboards import reply
from abc import abstractmethod

import random
import enum

class base_user_state():
    name: str
    tree: 'states_tree'

    def __init__(self, name: str, tree: 'states_tree'):
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

class states_tree():
    states: list[base_user_state] = []
    current_state: int = 0
    id: str
    user: 'User'

    def __init__(self, id: str, user: 'User'):
        self.user = user
        self.id = id

    def add_state(self, s: base_user_state) -> None:
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

class main_menu_sate(base_user_state):
    def __init__(self, tree: states_tree):
        super().__init__('main_menu', tree)

    async def process_message(self, message: Message):
        if message.text == 'Номер 4':
            await self.tree.set_state_by_name('orthoepy')
            return 

    async def enable(self):
        await self.tree.user.bot.send_message(
            chat_id=self.tree.id, 
            text='Вы в главном меню. Выберите функцию.',
            reply_markup=reply.main_menu_kb)
    
    async def disable(self):
        ...

class OrthoepyState(base_user_state):
    sub_state : SubState = SubState.MENU
    count: int = 0

    def __init__(self, tree: states_tree):
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
            text='Орфоэпия меню. ', 
            reply_markup=reply.orthoepy_menu_kb)
    
    async def disable(self):
        ...
from aiogram import Bot
from aiogram.types import Message

from src.models.user_states import (
    StatesTree,
    MainMenuState,
    OrthoepyState,
    SyntacticNormsAndRules
)

class UserData():
    orthoepy_record = 0
    syntactic_norms_and_rules_record = 0

class User():
    id: str
    tree: StatesTree
    bot: Bot
    data: UserData = UserData()

    def __init__(self, id: str, bot: Bot) -> None:
        self.id = id
        self.bot = bot
        self.tree = StatesTree(id, self)
        
    async def setup_tree(self):
        mms = MainMenuState(self.tree)
        orth = OrthoepyState(self.tree)
        snar = SyntacticNormsAndRules(self.tree)
        self.tree.add_state(mms)
        self.tree.add_state(orth)
        self.tree.add_state(snar)

    async def new_message(self, message: Message):
        await self.tree.execute_current_state(message)

    async def enable_first_state(self):
        await self.tree.states[0].enable()

    def __eq__(self, other: 'User') -> bool:
        return self.id == other.id

class UsersStorage():
    users: list[User] = []
    bot: Bot

    async def get_user(self, id: str) -> User:
        for user in self.users:
            if user.id == id:
                return user
        user = User(id, self.bot)
        await user.setup_tree()
        self.users.append(user)
        return user
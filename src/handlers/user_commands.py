from aiogram import Router

from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from src.models.user import User, UsersStorage

users_storage = UsersStorage()

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    user = await users_storage.get_user(message.from_user.id)
    await user.enable_first_state()

@router.message()
async def on_message(message: Message):
    user = await users_storage.get_user(message.from_user.id)
    await user.new_message(message)
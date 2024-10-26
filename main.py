import asyncio

from aiogram import Bot, Dispatcher

from config_reader import config
from src.handlers.user_commands import users_storage
from src.handlers import user_commands

async def main():
    bot = Bot(config.bot_token.get_secret_value())
    dp = Dispatcher()
    users_storage.bot = bot
    dp.include_routers(
        user_commands.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    print("Bot is running.")
    asyncio.run(main())
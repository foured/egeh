from aiogram.types import(
    ReplyKeyboardMarkup,
    KeyboardButton
)

main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Номер 4')
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

restart_back_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Заново'),
            KeyboardButton(text='Назад')
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

orthoepy_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Начать'),
            KeyboardButton(text='Рекорд'),
            KeyboardButton(text='Все слова')
        ],
        [
            KeyboardButton(text='Назад')
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
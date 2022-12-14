import asyncio
from aiogram import types
from bot.profiles import Profile
from bot.handlers import ACTIVITY_FIELDS


async def set_bot_commands(dispatcher):  # dispatcher: Dispatcher
    await dispatcher.bot.set_my_commands(
        [
            types.BotCommand("terms", "Создать Terms of Use"),
            types.BotCommand("privacy", "Создать Privacy Policy")
        ]
    )


async def cmd_start(message: types.Message):
    await message.answer("Здравствуйте! Для старта работы просим пройти анкетирование")
    await asyncio.sleep(1)
    await Profile.activity_field.set()
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
        keyboard=[[types.KeyboardButton(text=field)] for field in ACTIVITY_FIELDS]
    )
    await message.answer("Ваша сфера деятельности:", reply_markup=keyboard)

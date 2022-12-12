from aiogram import Dispatcher, Bot, executor
from aiogram.contrib.fsm_storage.files import JSONStorage
from bot.settings import BOT_STORAGE
from bot.dispatcher import on_startup, on_shutdown


def start_bot():
    bot = Bot("5988906998:AAGLqYyD6VbRouIm8wpSnBZ9mScH-S8CGIc")
    dispatcher = Dispatcher(bot, storage=JSONStorage(BOT_STORAGE))
    executor.start_polling(dispatcher, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)

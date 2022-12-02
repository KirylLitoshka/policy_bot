import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from bot.profiles import Profile, User

ACTIVITY_FIELDS = [
    "Разработчик",
    "Арбитражник",
    "Совмещаю"
]
APPLICATION_TYPES = [
    "Серое (Вьюхи под СРА офферы)",
    "Приложения с монетизацией рекламой",
    "Приложения с монетизацией подпиской",
    "Gamedev",
    "Работаем со всеми приложениями которые видим"
]


async def echo(message: types.Message):
    await message.answer(text=message.text)


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


async def process_activity_field(message: types.Message, state: FSMContext):
    """
    Устанавливает сферу деятельности и возвращает сообщение с выборкой ниши приложений
    :param message:
    :param state:
    :return:
    """
    async with state.proxy() as data:
        data['activity_field'] = message.text

    await Profile.next()
    await asyncio.sleep(1)
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
        keyboard=[[types.KeyboardButton(text=application)] for application in APPLICATION_TYPES]
    )
    await message.answer(f"Выберите нишу приложений:", reply_markup=keyboard)


async def process_application_type(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["application_type"] = message.text
    await Profile.next()
    await asyncio.sleep(1)
    await message.answer("Промокод", reply_markup=types.ReplyKeyboardRemove())


async def process_promo_code(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["promo_code"] = message.text
    await message.answer("Спасибо за прохождение анкетирования!")
    await asyncio.sleep(1)
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Создать Privacy Policy")],
            [types.KeyboardButton(text="Создать Terms of Use")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Продолжите фразу: «Сегодня я хочу...»", reply_markup=keyboard)
    await state.set_state("*")


async def process_username(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text

    await Profile.next()
    await asyncio.sleep(1)
    await message.answer("Введите название приложения:")


async def process_application_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["application_name"] = message.text
    await Profile.next()
    await asyncio.sleep(1)
    await message.answer("Введите ваш email:")


async def process_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["mail"] = message.text
    await state.set_state("*")


async def create_privacy_policy(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if "name" not in data:
            await Profile.name.set()
            return await message.answer("Введите ваше имя:", reply_markup=types.ReplyKeyboardRemove())


async def create_terms_of_use(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if "name" not in data:
            await Profile.name.set()
            return await message.answer("Введите ваше имя:", reply_markup=types.ReplyKeyboardRemove())


async def process_error(message: types.Message):
    """
    Удаляет сообщение если оно не в пуле выборки сферы деятельности
    :param message:
    :return coroutine:
    """
    return await message.delete()

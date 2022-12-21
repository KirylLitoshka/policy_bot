import asyncio
from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from bot.profiles import Profile, User
from bot.utils import build_policy, build_terms_of_use

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


async def process_activity_field(message: types.Message, state: FSMContext):
    """
    Устанавливает сферу деятельности и возвращает сообщение с выборкой ниши приложений
    :param message:
    :param state:
    :return:
    """
    async with state.proxy() as data:
        data['activity_field'] = message.text
        data["user_id"] = str(message.from_user.id)

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
    await message.answer("Промокод (???)", reply_markup=types.ReplyKeyboardRemove())


async def process_promo_code(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["promo_code"] = message.text
    await message.answer("Спасибо за прохождение анкетирования!")
    await main_menu(message, state)


async def main_menu(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    await asyncio.sleep(1)
    async with state.proxy() as data:
        data.pop("is_policy_created", None)
        data.pop("is_terms_created", None)
        data.pop("name", None)
    if isinstance(message, types.CallbackQuery):
        message = message.message
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


async def create_terms_of_use(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state != "*":
        return await message.delete()

    async with state.proxy() as data:
        data["current_document_type"] = "terms"
        data["is_terms_created"] = False
        user_id = data['user_id']
        if data.get("is_terms_created"):
            del data['name']
        if "name" not in data:
            return await set_user_name(message)
        user_data = data.as_dict()
        terms_link = await build_terms_of_use(user_data)
        if not terms_link:
            raise
        data["is_terms_created"] = True

    await message.bot.send_message(user_id, terms_link)
    await asyncio.sleep(1)
    await final_message(message, state)


async def create_privacy_policy(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    if isinstance(message, types.CallbackQuery):
        message = message.message
    current_state = await state.get_state()
    if current_state != "*":
        return await message.delete()

    async with state.proxy() as data:
        user_id = data['user_id']
        data["current_document_type"] = "policy"
        data["is_policy_created"] = False
        if data.get("is_policy_created"):
            del data["name"]
        if "name" not in data:
            return await set_user_name(message)
        user_data = data.as_dict()
        policy_link = await build_policy(user_data)
        if not policy_link:
            raise
        data["is_policy_created"] = True

    await message.bot.send_message(user_id, policy_link)
    await asyncio.sleep(1)
    await final_message(message, state)


async def final_message(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    if isinstance(message, types.CallbackQuery):
        message = message.message
    async with state.proxy() as data:
        is_policy_created = data.get("is_policy_created")
        is_terms_created = data.get("is_terms_created")
        if is_policy_created and is_terms_created:
            return await main_menu(message, state)
        elif is_policy_created:
            output_message = "Желаете создать Terms of Use?"
            callback_data = "terms"
        elif is_terms_created:
            output_message = "Желаете создать Privacy Policy?"
            callback_data = "privacy"

    await message.answer(
        text=output_message,
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[
            types.InlineKeyboardButton("Да", callback_data=callback_data),
            types.InlineKeyboardButton("Нет", callback_data="menu")
        ]])
    )


async def set_user_name(message: types.Message):
    await User.name.set()
    await message.answer("Введите ваше имя:", reply_markup=types.ReplyKeyboardRemove())


async def process_username(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text
    await User.next()
    await asyncio.sleep(1)
    await message.answer("Введите название приложения:")


async def process_application_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["application_name"] = message.text
    await User.next()
    await asyncio.sleep(1)
    await message.answer("Введите ваш email:")


async def process_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["mail"] = message.text
        current_document = data["current_document_type"]
        await state.set_state("*")
    if current_document == "terms":
        return await create_terms_of_use(message, state)
    elif current_document == "policy":
        return await create_privacy_policy(message, state)


async def process_error(message: types.Message):
    """
    Удаляет сообщение если оно не в пуле выборки сферы деятельности
    :param message:
    :return coroutine:
    """
    return await message.delete()

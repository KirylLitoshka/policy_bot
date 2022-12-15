import asyncio
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


async def create_files(message, state):
    current_state = await state.get_state()
    if current_state != "*":
        return await message.delete()

    if "terms" in message.text.lower():
        callback = build_terms_of_use
        document_type = "terms"
        output_message = "Желаете создать Privacy Policy?"
    elif "privacy" in message.text.lower():
        callback = build_policy
        document_type = "privacy"
        output_message = "Желаете создать Terms of Use?"
    else:
        raise

    async with state.proxy() as data:
        if "name" not in data:
            data["document_type"] = document_type
            return await set_user_name(message)
        user_data = data.as_dict()
        del data["name"]

    terms_link = await callback(user_data)

    await message.answer(terms_link)
    await asyncio.sleep(1)
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[[
            types.InlineKeyboardButton("Да", callback_data=document_type),
            types.InlineKeyboardButton("Нет", callback_data="finish")
        ]]
    )
    return await message.answer(output_message, reply_markup=keyboard)


async def set_user_name(message):
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
        if not data.get("document_type"):
            raise
        message.text = data.pop("document_type")
        await state.set_state("*")
    return await create_files(message, state)


async def process_error(message: types.Message):
    """
    Удаляет сообщение если оно не в пуле выборки сферы деятельности
    :param message:
    :return coroutine:
    """
    return await message.delete()


async def create_by_callback_data(query, state):
    return await create_files(query.message, state)


async def finish(query, state):
    await state.set_state("*")
    final_message = """
Ваш документ готов. Вы можете создать и другие документы:
✔️Privacy Policy при помощи команды /privacy
✔️Terms of use при помощи команды /terms
    """
    if isinstance(query, types.CallbackQuery):
        await query.message.answer(final_message)
    else:
        await query.answer(final_message)

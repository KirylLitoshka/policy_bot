from aiogram.dispatcher.filters.state import StatesGroup, State


class Profile(StatesGroup):
    activity_field = State()
    application_types = State()
    promo_code = State()


class User(StatesGroup):
    name = State()
    application_name = State()
    mail = State()

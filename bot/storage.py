import datetime

import aiofiles
import os
import json
from aiogram import types, Dispatcher
from bot.utils import get_referral_type
from bot.settings import STORAGE_DIR


def load_users(storage_dir: str):
    users_data = {}
    users_storage = os.path.join(storage_dir, "users")
    if not os.path.exists(users_storage):
        os.makedirs(users_storage)
        return users_data
    *_, users_files = list(*os.walk(users_storage))
    if not users_files:
        return users_data
    for user_file_name in users_files:
        user_id = user_file_name.split(".")[0]
        with open(f"{users_storage}/{user_file_name}", encoding="utf8") as fp:
            file_data = json.loads(fp.read())
            users_data[user_id] = file_data
    return users_data


async def save_user(dispatcher: Dispatcher, user: dict):
    user_id = user["id"]
    dispatcher.data['users'][user_id] = user
    async with aiofiles.open(f'{STORAGE_DIR}/users/{user_id}.json', mode="w") as fp:
        await fp.write(json.dumps(user, indent=4, ensure_ascii=False))


async def create_new_user(message: types.Message):
    user_id = str(message.from_user.id)
    dispatcher = Dispatcher.get_current()
    if user_id in dispatcher.data["users"]:
        return
    current_time = datetime.datetime.now()
    timestamp = str(int(current_time.timestamp()))
    user_ref = get_referral_type(message.text)
    user = {
        "id": user_id,
        "referral_type": user_ref,
        "created": timestamp
    }
    await save_user(dispatcher, user)

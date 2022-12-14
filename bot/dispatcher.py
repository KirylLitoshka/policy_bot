from bot.commands import cmd_start, set_bot_commands
from bot.utils import get_google_token
from bot.handlers import *


async def on_startup(dp):
    await set_bot_commands(dp)
    dp.data['google_api_key'] = get_google_token()
    dp.register_message_handler(cmd_start, commands=["start"])
    dp.register_message_handler(create_terms_of_use, commands=["terms"], state="*")
    dp.register_message_handler(create_privacy_policy, commands=["privacy"], state="*")
    dp.register_callback_query_handler(finish, lambda msg: msg.data == "finish", state="*")
    dp.register_callback_query_handler(
        create_by_callback_data, lambda msg: msg.data == "privacy" or msg.data == "terms", state="*"
    )
    dp.register_message_handler(
        process_activity_field, lambda msg: msg.text in ACTIVITY_FIELDS, state=Profile.activity_field
    )
    dp.register_message_handler(
        process_error, lambda msg: msg.text not in ACTIVITY_FIELDS, state=Profile.activity_field
    )
    dp.register_message_handler(
        process_application_type, lambda msg: msg.text in APPLICATION_TYPES, state=Profile.application_types
    )
    dp.register_message_handler(
        process_error, lambda msg: msg.text not in APPLICATION_TYPES, state=Profile.application_types
    )
    dp.register_message_handler(process_username, state=User.name)
    dp.register_message_handler(process_application_name, state=User.application_name)
    dp.register_message_handler(process_email, state=User.mail)
    dp.register_message_handler(process_promo_code, state=Profile.promo_code)
    dp.register_message_handler(create_terms_of_use, lambda msg: msg.text == "Создать Terms of Use", state="*")
    dp.register_message_handler(create_privacy_policy, lambda msg: msg.text == "Создать Privacy Policy", state="*")


async def on_shutdown(dp):
    pass

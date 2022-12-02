from bot.handlers import *


async def on_startup(dp):
    dp.register_message_handler(cmd_start, commands=["start"])
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
    dp.register_message_handler(process_promo_code, state=Profile.promo_code)
    dp.register_message_handler(create_terms_of_use, lambda msg: msg.text == "Создать Terms of Use", state="*")
    dp.register_message_handler(create_privacy_policy, lambda msg: msg.text == "Создать Privacy Policy", state="*")


async def on_shutdown(dp):
    pass

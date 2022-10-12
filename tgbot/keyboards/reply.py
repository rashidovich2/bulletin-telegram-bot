from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from tgbot.config import Config


def get_menu(cfg: Config):
    buttons_text = cfg.misc.texts.buttons

    menu = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=buttons_text.rent),
                KeyboardButton(text=buttons_text.sell)
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    return menu

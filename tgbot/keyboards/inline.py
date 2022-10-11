from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from tgbot.config import Config

new_cost_cd = CallbackData("new_cost", "ad_type", "category")

ad_cd = CallbackData("post_ad", "level", "category", "ad_id")
photo_cd = CallbackData("photo", "ad_id")
get_photo_cd = CallbackData("get_photo", "ad_id")
delete_photo_cd = CallbackData("delete_photo", "ad_id")
desc_cd = CallbackData("desc", "ad_id")
cost_cd = CallbackData("cost", "ad_id")
publish_cd = CallbackData("publish", "ad_id")
confirm_publish_cd = CallbackData("confirm_publish", "ad_id", "confirm")
revoke_cd = CallbackData("cancel_publish", "ad_id")


def make_callback_data(level, category, ad_id):
    return ad_cd.new(level=level, category=category, ad_id=ad_id)


async def ad_categories_keyboard(cfg: Config, ad_type):
    markup = InlineKeyboardMarkup()

    categories = cfg.misc.texts.object_types
    for category in categories:
        button_text = f"{category}"
        callback_data = new_cost_cd.new(
            ad_type=ad_type,
            category=str(categories.index(category))
        )
        markup.row(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )

    return markup


async def ad_categories_change_keyboard(cfg: Config, ad_id):
    CURRENT_LEVEL = 0
    markup = InlineKeyboardMarkup()

    categories = cfg.misc.texts.object_types
    for category in categories:
        button_text = f"{category}"
        callback_data = make_callback_data(
            level=CURRENT_LEVEL + 1,
            category=str(categories.index(category)),
            ad_id=ad_id
        )
        markup.row(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )

    return markup


async def photo_navigate(cfg: Config, ad_id, category):
    markup = InlineKeyboardMarkup()

    callback_data = make_callback_data(level=1, ad_id=ad_id, category=category)
    markup.row(
        InlineKeyboardButton(text=cfg.misc.texts.buttons.ready, callback_data=callback_data)
    )

    return markup


async def revoke_button(cfg: Config, ad_id):
    markup = InlineKeyboardMarkup()

    markup.row(
        InlineKeyboardButton(
            text=cfg.misc.texts.buttons.revoke,
            callback_data=revoke_cd.new(ad_id=ad_id)
        )
    )

    return markup


async def confirm_buttons(cfg: Config, ad_id):
    markup = InlineKeyboardMarkup()

    markup.row(
        InlineKeyboardButton(text="Да", callback_data=confirm_publish_cd.new(ad_id=ad_id, confirm="1")),
        InlineKeyboardButton(text="Нет", callback_data=confirm_publish_cd.new(ad_id=ad_id, confirm="0")),
    )

    return markup


async def ad_navigate(cfg: Config, ad_id, category, photo="0"):
    CURRENT_LEVEL = 1
    markup = InlineKeyboardMarkup()

    if photo == "0":
        photo_text = cfg.misc.texts.buttons.add_photo
    else:
        photo_text = cfg.misc.texts.buttons.edit_photo

    photo_markup = InlineKeyboardButton(
        text=photo_text,
        callback_data=photo_cd.new(ad_id=ad_id)
    )

    show_photo_markup = InlineKeyboardButton(
        text=cfg.misc.texts.buttons.show_photo,
        callback_data=get_photo_cd.new(ad_id=ad_id)
    )

    delete_photo_markup = InlineKeyboardMarkup(
        text=cfg.misc.texts.buttons.delete_photo,
        callback_data=delete_photo_cd.new(ad_id=ad_id)
    )

    description_markup = InlineKeyboardButton(
        text=cfg.misc.texts.buttons.edit_description,
        callback_data=desc_cd.new(ad_id=ad_id)
    )

    cost_markup = InlineKeyboardButton(
        text=cfg.misc.texts.buttons.edit_cost,
        callback_data=cost_cd.new(ad_id=ad_id)
    )

    category_markup = InlineKeyboardButton(
        text=cfg.misc.texts.buttons.edit_category,
        callback_data=make_callback_data(
            level=CURRENT_LEVEL - 1,
            category=str(category),
            ad_id=ad_id
        )
    )

    publish_markup = InlineKeyboardMarkup(
        text=cfg.misc.texts.buttons.publish,
        callback_data=publish_cd.new(ad_id=ad_id)
    )

    if photo != "0":
        markup.row(show_photo_markup, delete_photo_markup)
    markup.row(photo_markup, description_markup)
    markup.row(cost_markup, category_markup)
    markup.row(publish_markup)

    return markup

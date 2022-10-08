from aiogram import Dispatcher
from aiogram.dispatcher.handler import ctx_data
from aiogram.types import Message

from tgbot.config import Config
from tgbot.keyboards.reply import get_menu


async def user_start(message: Message):
    cfg: Config = ctx_data.get()['config']
    menu = get_menu(cfg)
    await message.reply(cfg.misc.texts.messages.start_msg, reply_markup=menu)


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")

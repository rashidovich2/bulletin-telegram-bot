from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

from tgbot.config import Config


class ChannelJoinedMiddleware(BaseMiddleware):
    def __init__(self, config: Config):
        super().__init__()
        self.cfg = config

    async def on_process_message(self, message: types.Message, data: dict):
        cfg: Config = self.cfg
        member = await message.bot.get_chat_member(cfg.tg_bot.channel_id, message.from_user.id)

        if member.status == "left" or member.status == "kicked" or member.status == "restricted":
            channel_href = f"t.me/{cfg.tg_bot.channel_tag}"

            await message.answer(
                text=cfg.misc.texts.messages.not_in_channel_msg.format(channel_href)
            )
            raise CancelHandler()

from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from cachetools import TTLCache

from tgbot.config import Config

channel_joined_member_cache = TTLCache(maxsize=1000, ttl=300)


def is_member_in_channel(member: types.ChatMember) -> bool:
    if member.status == "left" or member.status == "kicked" or member.status == "restricted":
        return False
    return True


async def get_channel_member(cfg: Config, message: types.Message) -> types.ChatMember:
    return await message.bot.get_chat_member(cfg.channel.id, message.from_user.id)


async def get_cache_channel_member(cfg: Config, message: types.Message) -> types.ChatMember:
    chat_id = message.from_user.id

    if chat_id in channel_joined_member_cache:
        return channel_joined_member_cache[chat_id]

    member = await get_channel_member(cfg, message)

    if is_member_in_channel(member):
        channel_joined_member_cache[chat_id] = member

    return member


class ChannelJoinedMiddleware(BaseMiddleware):
    def __init__(self, config: Config):
        super().__init__()
        self.cfg = config

    async def on_process_message(self, message: types.Message, data: dict):
        cfg: Config = self.cfg

        member = await get_channel_member(cfg, message)

        if not is_member_in_channel(member):
            await message.answer(
                text=cfg.misc.texts.messages.not_in_channel_msg.format(cfg.channel.url)
            )
            raise CancelHandler()

import asyncio
import logging

import asyncpg
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.echo import register_echo
from tgbot.handlers.user import register_user
from tgbot.middlewares.channel_joined import ChannelJoinedMiddleware
from tgbot.middlewares.environment import EnvironmentMiddleware
from tgbot.middlewares.postgres_db import PostgresDbMiddleware

logger = logging.getLogger(__name__)


async def register_all_middlewares(dp, config):
    pool = await asyncpg.create_pool(dsn=config.db.postgres_dsn)

    dp.setup_middleware(EnvironmentMiddleware(config=config))
    dp.setup_middleware(ChannelJoinedMiddleware(config=config))
    dp.setup_middleware(PostgresDbMiddleware(pool=pool))

    # Migrations
    fd = open("create_db.sql", 'r')
    sqlFile = fd.read()
    fd.close()

    conn = await asyncpg.connect(dsn=config.db.postgres_dsn)
    grant_privileges_sql = f"ALTER TABLE IF EXISTS ads OWNER TO {config.db.user};" \
                           f"GRANT ALL PRIVILEGES ON DATABASE {config.db.database} to {config.db.user};" \
                           f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {config.db.user};" \
                           f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {config.db.user};"

    await conn.execute(grant_privileges_sql)
    await conn.execute(sqlFile)
    await conn.execute(grant_privileges_sql)

    await conn.close()


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp, cfg):
    # register_admin(dp)
    register_user(dp, cfg)

    # register_echo(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env", "texts.yml")

    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)

    await config.channel.set_channel_info(bot)

    bot['config'] = config

    await register_all_middlewares(dp, config)
    register_all_filters(dp)
    register_all_handlers(dp, config)

    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")

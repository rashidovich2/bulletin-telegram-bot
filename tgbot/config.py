from dataclasses import dataclass

import yaml
from environs import Env


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str
    port: int
    postgres_dsn: str

    def __init__(self, host, password, user, database, port):
        self.host = host
        self.password = password
        self.user = user
        self.database = database
        self.port = port

        postgres_dsn = f"postgres://{user}:{password}@{host}:{port}/{database}"
        self.postgres_dsn = postgres_dsn


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    use_redis: bool


# Texts classes
@dataclass
class ButtonsTexts:
    rent: str
    sell: str
    inline_back: str
    inline_forward: str


@dataclass
class MessagesPartsText:
    what_object: str
    cost: str
    photo: str
    description: str


@dataclass
class MessagesText:
    start_msg: str
    success_msg: str
    parts: MessagesPartsText


@dataclass
class Texts:
    object_types: list[str]
    buttons: ButtonsTexts
    messages: MessagesText


# Config
@dataclass
class Miscellaneous:
    texts: Texts
    other_params: str = None


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Miscellaneous


def load_config(path: str = None, texts_path=None):
    env = Env()
    env.read_env(path)

    texts = None

    if texts_path is not None:
        with open(texts_path, "r", encoding="utf-8") as stream:
            try:
                texts = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS"),
        ),
        db=DbConfig(
            host=env.str('DB_HOST'),
            password=env.str('DB_PASS'),
            user=env.str('DB_USER'),
            database=env.str('DB_NAME'),
            port=env.int('DB_PORT')
        ),
        misc=Miscellaneous(
            texts=Texts(
                object_types=texts['object_types'],
                buttons=ButtonsTexts(
                    rent=texts['buttons']['rent'],
                    sell=texts['buttons']['sell'],
                    inline_back=texts['buttons']['inline_back'],
                    inline_forward=texts['buttons']['inline_forward']
                ),
                messages=MessagesText(
                    start_msg=texts['messages']['start_msg'],
                    success_msg=texts['messages']['success_msg'],
                    parts=MessagesPartsText(
                        what_object=texts['messages']['parts']['what_object'],
                        cost=texts['messages']['parts']['cost'],
                        photo=texts['messages']['parts']['photo'],
                        description=texts['messages']['parts']['description']
                    )
                )
            )
        ),

    )

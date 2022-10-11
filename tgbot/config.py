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
    channel_id: int
    channel_tag: str
    token: str
    admin_ids: list[int]
    use_redis: bool


# Texts classes
@dataclass
class ButtonsTexts:
    rent: str
    sell: str
    last_ad: str
    publish: str
    revoke: str
    add_photo: str
    show_photo: str
    delete_photo: str
    edit_photo: str
    edit_description: str
    edit_cost: str
    edit_category: str
    cancel: str
    ready: str


@dataclass
class MessagesPartsText:
    what_object: str
    cost: str
    photo: str
    description: str


@dataclass
class MessagesText:
    sell: str
    rent: str
    confirm: str
    confirm_declined: str
    start_msg: str
    success_msg: str
    revoked_msg: str
    cannot_revoke: str
    not_in_channel_msg: str
    ad_already_published_msg: str
    parts: MessagesPartsText


@dataclass()
class DescriptionLengths:
    error_message: str
    min: int
    max: int


@dataclass()
class Lenghts:
    description: DescriptionLengths


@dataclass
class Texts:
    object_types: list[str]
    buttons: ButtonsTexts
    messages: MessagesText
    lengths: Lenghts
    ad_message: str


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
            channel_id=env.int("CHANNEL_ID"),
            channel_tag=env.str("CHANNEL_TAG"),
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
                    last_ad=texts['buttons']['last_ad'],
                    publish=texts['buttons']['publish'],
                    revoke=texts['buttons']['revoke'],
                    add_photo=texts['buttons']['add_photo'],
                    show_photo=texts['buttons']['show_photo'],
                    delete_photo=texts['buttons']['delete_photo'],
                    edit_photo=texts['buttons']['edit_photo'],
                    edit_description=texts['buttons']['edit_description'],
                    edit_cost=texts['buttons']['edit_cost'],
                    edit_category=texts['buttons']['edit_category'],
                    cancel=texts['buttons']['cancel'],
                    ready=texts['buttons']['ready']
                ),
                messages=MessagesText(
                    sell=texts['messages']['sell'],
                    rent=texts['messages']['rent'],
                    confirm=texts['messages']['confirm'],
                    confirm_declined=texts['messages']['confirm_declined'],
                    start_msg=texts['messages']['start_msg'],
                    success_msg=texts['messages']['success_msg'],
                    revoked_msg=texts['messages']['revoked_msg'],
                    cannot_revoke=texts['messages']['cannot_revoke'],
                    not_in_channel_msg=texts['messages']['not_in_channel_msg'],
                    ad_already_published_msg=texts['messages']['ad_already_published_msg'],
                    parts=MessagesPartsText(
                        what_object=texts['messages']['parts']['what_object'],
                        cost=texts['messages']['parts']['cost'],
                        photo=texts['messages']['parts']['photo'],
                        description=texts['messages']['parts']['description']
                    )
                ),
                lengths=Lenghts(
                    description=DescriptionLengths(
                        error_message=texts['lengths']['description']['error_message'],
                        min=texts['lengths']['description']['min'],
                        max=texts['lengths']['description']['max']
                    )
                ),
                ad_message=texts['ad_message'],
            )
        ),

    )

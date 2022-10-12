from aiogram.types import User

from tgbot.config import Config
from tgbot.models.ad import Ad


def format_thousands_cost(cost: str):
    rev_cost = cost[::-1]
    rev_new_cost = ""

    counter = 1
    for i in range(len(rev_cost)):
        rev_new_cost += rev_cost[i]
        if counter == 3:
            counter = 1
            rev_new_cost += " "
        else:
            counter += 1

    return rev_new_cost[::-1]


def make_info_text(cfg: Config, ad: Ad, from_user: User) -> str:
    if ad.ad_type == "rent":
        ad_type = cfg.misc.texts.messages.rent
    else:
        ad_type = cfg.misc.texts.messages.sell

    name = ""

    if from_user.first_name is not None:
        name += from_user.first_name

    if from_user.last_name is not None:
        if name != "":
            name += " "
        name += from_user.last_name

    href = f"tg://user?id={from_user.id}"

    return cfg.misc.texts.ad_message.format(
        ad_type,
        ad.category,
        ad.description,
        format_thousands_cost(str(ad.cost)),
        href,
        name,
        cfg.channel.url,
        cfg.channel.title
    )


def get_category_with_index(cfg: Config, category_index: str) -> str:
    index = int(category_index)

    return cfg.misc.texts.object_types[index]

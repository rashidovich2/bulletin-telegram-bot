from aiogram.types import User

from tgbot.config import Config
from tgbot.models.ad import Ad
import smtplib
from email.mime.text import MIMEText


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


def send_mail(cfg: Config, ad: Ad, from_user: User, ad_href):
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

    name = ""

    if from_user.first_name is not None:
        name += from_user.first_name

    if from_user.last_name is not None:
        if name != "":
            name += " "
        name += from_user.last_name

    # f"Ссылка на объявление: <a href=\"{ad_href}\">Перейти</a><br><br>" \
    text = f"<b>{ad_type}</b><br>" \
           f"Объект: <b>{ad.category}</b><br><br>" \
           f"{ad.description}<br><br>" \
           f"Цена: <b>{format_thousands_cost(str(ad.cost))} ₽</b><br>"

    if from_user.username is not None:
        user_href = f"t.me/{from_user.username}"
        text = text + f"Прислано: <a href={user_href}>{name}</a> [TelegramID: <b>{from_user.id}</b>]"
    else:
        text = text + f"Прислано: {name} (Не проставлен username) [TelegramID: <b>{from_user.id}</b>]"

    msg = MIMEText(text, 'html')
    msg['Subject'] = f'Новое объявление от {name} на канале {cfg.channel.title}'
    msg['From'] = cfg.smtp.user
    msg['To'] = cfg.misc.email

    s = smtplib.SMTP_SSL(cfg.smtp.host, cfg.smtp.port)
    s.set_debuglevel(1)
    s.ehlo()
    s.login(user=cfg.smtp.user, password=cfg.smtp.password)
    s.auth_plain()
    s.sendmail(cfg.smtp.user, [cfg.misc.email], msg.as_string())
    s.quit()


def get_category_with_index(cfg: Config, category_index: str) -> str:
    index = int(category_index)

    return cfg.misc.texts.object_types[index]

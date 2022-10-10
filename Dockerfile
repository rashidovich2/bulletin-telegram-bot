FROM python:3.9-buster
ENV BOT_NAME=$BOT_NAME

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app
RUN pip install -r /usr/src/app/requirements.txt

COPY bot.py /usr/src/app
COPY tgbot /usr/src/app
COPY texts.yml /usr/src/app

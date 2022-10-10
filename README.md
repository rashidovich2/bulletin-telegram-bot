# Bulletin bot [Aiogram Python]

Телеграм бот для выкладывания объявлений пользователей [Aiogram + Python]

## Environment
```env
# Prefix for container names
BOT_CONTAINER_NAME=bot_container_name
# Prefix for container image names
BOT_IMAGE_NAME=botimage_name
# Bot name
BOT_NAME=mybotname
# Telegram bot token, get from @BotFather
BOT_TOKEN=123456:Your-TokEn_ExaMple
# Admin telegram chat id's
ADMINS=123456,654321
# Telegram channel id, which get ads
CHANNEL_ID=-123456789
# Telegram channel name (tag), for make href links
CHANNEL_TAG=channel_tag

# Db Settings (Only supports Postgres)
DB_USER=exampleDBUserName
DB_PASS=exampleDBPassword
DB_NAME=exampleDBName
DB_HOST=db # If use our docker-compose, not changed this!
DB_PORT=5432
```

## Only first start
```sh
docker-compose up -d --build
docker exec -it <PASS BOT_CONTAINER_NAME>-db bash
psql -U <PASS DB_USER> -d <PASS DB_NAME> -f /create_db.sql
```

## Restart
```sh
docker-compose down
docker-compose up -d --build
```

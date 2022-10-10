from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.handler import ctx_data
from aiogram.types import Message, CallbackQuery, MediaGroup, InputFile, InputMediaPhoto

from tgbot.config import Config
from tgbot.keyboards.inline import ad_categories_keyboard, ad_navigate, ad_cd, photo_cd, desc_cd, cost_cd, \
    new_cost_cd, \
    ad_categories_change_keyboard, photo_navigate, get_photo_cd, delete_photo_cd, publish_cd, revoke_button, revoke_cd, \
    confirm_publish_cd, confirm_buttons
from tgbot.keyboards.reply import get_menu
from tgbot.misc.utils import get_category_with_index, make_info_text
from tgbot.services.repository import Repo


async def user_start(message: Message):
    cfg: Config = ctx_data.get()['config']
    menu = get_menu(cfg)
    await message.reply(cfg.misc.texts.messages.start_msg, reply_markup=menu)


async def sell_command(message: Message):
    cfg: Config = ctx_data.get()['config']

    inline_markup = await ad_categories_keyboard(cfg, "sell")

    await message.answer(text=cfg.misc.texts.messages.parts.what_object, reply_markup=inline_markup)


async def rent_command(message: Message):
    cfg: Config = ctx_data.get()['config']

    inline_markup = await ad_categories_keyboard(cfg, "rent")

    await message.answer(text=cfg.misc.texts.messages.parts.what_object, reply_markup=inline_markup)


async def category_navigate(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    mw_data = ctx_data.get()
    cfg: Config = mw_data['config']
    repo: Repo = mw_data['repo']

    data = await state.get_data()
    photo_ids = []

    for key, value in data.items():
        if str(key).startswith("photo_"):
            photo_ids.append(value)

    category = callback_data.get("category")
    level = callback_data.get("level")
    ad_id = callback_data.get("ad_id")

    ad = await repo.get_ad(ad_id)

    if level == "0":
        inline_markup = await ad_categories_change_keyboard(cfg, ad.id)
    else:
        if len(photo_ids) > 0:
            mg = MediaGroup()
            for photo_id in photo_ids[:9]:
                mg.attach_photo(photo=photo_id)
            media_group = mg.to_python()
        else:
            media_group = ad.media_group

        ad = await repo.update_ad(
            ad_id=ad.id,
            ad_type=ad.ad_type,
            category=get_category_with_index(cfg, category),
            cost=ad.cost,
            description=ad.description,
            media_group=media_group
        )
        if len(ad.media_group) == 0:
            is_media = "0"
        else:
            is_media = "1"

        inline_markup = await ad_navigate(cfg, ad.id, category, is_media)

    await callback.answer()
    await callback.message.edit_text(text=make_info_text(cfg, ad, callback.from_user), reply_markup=inline_markup)
    await state.reset_state()


async def change_photo(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    mw_data = ctx_data.get()
    cfg: Config = mw_data['config']
    repo: Repo = mw_data['repo']

    ad_id = callback_data.get("ad_id")
    ad = await repo.get_ad(ad_id)

    await state.set_state("wait_new_photo")
    await state.update_data(ad_id=ad.id)

    ctgr = cfg.misc.texts.object_types.index(ad.category)

    markup = await photo_navigate(cfg, ad.id, ctgr)

    await callback.answer()
    await callback.message.edit_text(
        text=cfg.misc.texts.messages.parts.photo,
        reply_markup=markup,
    )


async def change_description(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    cfg: Config = ctx_data.get()['config']

    ad_id = callback_data.get("ad_id")

    await callback.answer()
    await state.set_state("wait_description")
    sended_msg = await callback.message.answer(text=cfg.misc.texts.messages.parts.description)

    data = await state.get_data()

    state_d_ids = data.get("delete_ids")
    delete_ids: list[int] = state_d_ids
    if delete_ids is None:
        delete_ids: list[int] = []
    delete_ids.append(sended_msg.message_id)

    await state.update_data(
        ad_id=ad_id,
        main_msg_id=callback.message.message_id,
        delete_ids=delete_ids
    )


async def change_cost(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    cfg: Config = ctx_data.get()['config']

    ad_id = callback_data.get("ad_id")

    await callback.answer()
    await state.set_state("wait_cost")
    sended_msg = await callback.message.answer(text=cfg.misc.texts.messages.parts.cost)

    data = await state.get_data()

    state_d_ids: list[int] = data.get("delete_ids")
    delete_ids: list[int] = state_d_ids
    if delete_ids is None:
        delete_ids: list[int] = []
    delete_ids.append(sended_msg.message_id)

    await state.update_data(
        ad_id=ad_id,
        main_msg_id=callback.message.message_id,
        delete_ids=delete_ids,
    )


async def wait_description(message: Message, state: FSMContext):
    mw_data = ctx_data.get()
    cfg: Config = mw_data['config']
    repo: Repo = mw_data['repo']

    data = await state.get_data()

    ad_id = data.get("ad_id")
    ad = await repo.get_ad(ad_id)

    main_msg_id = data.get("main_msg_id")

    delete_ids: list[int] = data.get("delete_ids")

    if len(ad.media_group) == 0:
        is_media = "0"
    else:
        is_media = "1"
    inline_markup = await ad_navigate(cfg, ad_id, cfg.misc.texts.object_types.index(ad.category), is_media)

    updated_ad = await repo.update_ad(
        ad_id=ad.id,
        ad_type=ad.ad_type,
        category=ad.category,
        cost=ad.cost,
        description=message.parse_entities(as_html=True),
        media_group=ad.media_group
    )

    await message.bot.edit_message_text(
        text=make_info_text(cfg, updated_ad, message.from_user),
        chat_id=message.chat.id,
        message_id=main_msg_id,
        reply_markup=inline_markup,
    )

    delete_ids.append(message.message_id)

    for delete_id in delete_ids:
        await message.bot.delete_message(message_id=delete_id, chat_id=message.chat.id)
    await state.reset_state()


async def wait_cost(message: Message, state: FSMContext):
    mw_data = ctx_data.get()
    cfg: Config = mw_data['config']
    repo: Repo = mw_data['repo']

    data = await state.get_data()
    ad_id = data.get("ad_id")

    ad = await repo.get_ad(ad_id)

    delete_ids: list[int] = data.get("delete_ids")

    try:
        main_msg_id = data.get("main_msg_id")
        cost = int(message.text)

        if cost < 0:
            msg = await message.answer("Цена не может быть отрицательной! Введите снова")
            delete_ids.append(msg.message_id)
            delete_ids.append(message.message_id)
            await state.update_data(delete_ids=delete_ids)
            return

        if len(ad.media_group) == 0:
            is_media = "0"
        else:
            is_media = "1"
        inline_markup = await ad_navigate(cfg, ad_id, cfg.misc.texts.object_types.index(ad.category), is_media)

        updated_ad = await repo.update_ad(
            ad_id=ad.id,
            ad_type=ad.ad_type,
            category=ad.category,
            cost=cost,
            description=ad.description,
            media_group=ad.media_group
        )

        await message.bot.edit_message_text(
            text=make_info_text(cfg, updated_ad, message.from_user),
            chat_id=message.chat.id,
            message_id=main_msg_id,
            reply_markup=inline_markup,
        )

        delete_ids.append(message.message_id)

        for delete_id in delete_ids:
            await message.bot.delete_message(message_id=delete_id, chat_id=message.chat.id)
        await state.reset_state()

    except ValueError:
        msg = await message.answer("Введите число!")
        delete_ids.append(msg.message_id)
        delete_ids.append(message.message_id)
        await state.update_data(delete_ids=delete_ids)

    except Exception:
        await message.answer("Ошибка, попробуйте заново!")
        await state.reset_state()


async def change_new_cost(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    cfg: Config = ctx_data.get()['config']

    ad_type = callback_data.get("ad_type")
    category = callback_data.get("category")

    await state.set_state("wait_new_cost")
    await state.update_data(
        ad_type=ad_type,
        category=category
    )

    await callback.answer()
    await callback.message.edit_text(text=cfg.misc.texts.messages.parts.cost)


async def wait_new_cost(message: Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']

    data = await state.get_data()
    ad_type = data.get("ad_type")
    category = data.get("category")

    try:
        cost = int(message.text)
        if cost <= 0:
            await message.answer("Введите число больше нуля!")
            return

        await state.reset_state()
        await state.set_state("wait_new_description")
        await state.update_data(
            ad_type=ad_type,
            category=category,
            cost=cost,
        )

        await message.answer(text=cfg.misc.texts.messages.parts.description)

    except ValueError:
        await message.answer("Введите число!")

    except Exception:
        await message.answer("Ошибка, попробуйте заново!")
        await state.reset_state()


async def wait_new_description(message: Message, state: FSMContext):
    mw_data = ctx_data.get()
    cfg: Config = mw_data['config']
    repo: Repo = mw_data['repo']

    data = await state.get_data()
    ad_type = data.get("ad_type")
    category = data.get("category")
    cost = data.get("cost")

    description = message.text
    description_ent = message.parse_entities(as_html=True)
    desc_lengths = cfg.misc.texts.lengths.description
    if desc_lengths.min > len(description) > desc_lengths.max:
        await message.answer(text=cfg.misc.texts.messages.parts.description)
        return

    new_ad = await repo.add_ad(
        user_id=message.from_user.id,
        ad_type=ad_type,
        category=get_category_with_index(cfg, category),
        cost=int(cost),
        description=description_ent
    )
    await state.reset_state()

    await state.set_state("wait_new_photo")
    await state.update_data(ad_id=new_ad.id)

    markup = await photo_navigate(cfg, new_ad.id, category)

    await message.answer(
        text=cfg.misc.texts.messages.parts.photo,
        reply_markup=markup,
    )


async def wait_new_photo(message: Message, state: FSMContext):
    async with state.proxy() as data:
        file_id = message.photo[-1].file_id
        additional_data = {str("photo_" + file_id): file_id}
        data.update(**additional_data)


async def show_photo(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    mw_data = ctx_data.get()
    repo: Repo = mw_data['repo']

    ad_id = callback_data.get("ad_id")
    ad = await repo.get_ad(ad_id)

    await callback.answer()
    await callback.message.reply_media_group(media=ad.media_group)


async def delete_photo(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    mw_data = ctx_data.get()
    cfg: Config = mw_data['config']
    repo: Repo = mw_data['repo']

    ad_id = callback_data.get("ad_id")
    ad = await repo.get_ad(ad_id)

    await repo.update_ad(
        ad_id=ad.id,
        ad_type=ad.ad_type,
        category=ad.category,
        cost=ad.cost,
        description=ad.description,
        media_group=[]
    )

    is_media = "0"
    ctrg = cfg.misc.texts.object_types.index(ad.category)

    inline_markup = await ad_navigate(cfg, ad.id, ctrg, is_media)

    await callback.answer()
    await callback.message.edit_text(
        text=make_info_text(cfg, ad, callback.from_user),
        reply_markup=inline_markup
    )


async def publish_ad(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    mw_data = ctx_data.get()
    cfg: Config = mw_data['config']
    repo: Repo = mw_data['repo']

    ad_id = callback_data.get("ad_id")
    ad = await repo.get_ad(ad_id)

    if len(ad.media_group) > 0:
        media_group = ad.media_group
        media_group[0]["caption"] = make_info_text(cfg, ad, callback.from_user)

        msgs = await callback.message.reply_media_group(
            media=media_group
        )
    else:
        msgs = []
        msg = await callback.message.answer(
            text=make_info_text(cfg, ad, callback.from_user)
        )
        msgs.append(msg)

    delete_msg_ids = []
    for msg in msgs:
        delete_msg_ids.append(msg.message_id)

    confirm_markup = await confirm_buttons(cfg, ad_id)

    await state.set_state("confirm_ad")
    await state.update_data(delete_ids=delete_msg_ids)
    await callback.answer()
    await callback.message.answer(
        text=cfg.misc.texts.messages.confirm,
        reply_markup=confirm_markup
    )


async def confirm_ad(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    mw_data = ctx_data.get()
    cfg: Config = mw_data['config']
    repo: Repo = mw_data['repo']

    ad_id = callback_data.get("ad_id")
    confirm = callback_data.get("confirm")

    data = await state.get_data()
    delete_ids: list[int] = data.get("delete_ids")
    delete_ids.append(callback.message.message_id)

    if confirm == "1":
        ad = await repo.get_ad(ad_id)

        if len(ad.media_group) > 0:
            media_group = ad.media_group
            media_group[0]["caption"] = make_info_text(cfg, ad, callback.from_user)

            channel_msgs = await callback.bot.send_media_group(
                chat_id=cfg.tg_bot.channel_id,
                media=media_group
            )
        else:
            channel_msgs = []
            channel_msg = await callback.bot.send_message(
                chat_id=cfg.tg_bot.channel_id,
                text=make_info_text(cfg, ad, callback.from_user)
            )
            channel_msgs.append(channel_msg)

        await repo.publish_ad(ad_id)

        href = f"t.me/{cfg.tg_bot.channel_tag}/{channel_msgs[0].message_id}"

        msg_ids = []
        for channel_msg in channel_msgs:
            msg_ids.append(str(channel_msg.message_id))

        delete_markup = await revoke_button(cfg, ad_id, msg_ids)

        for msg_id in delete_ids:
            await callback.bot.delete_message(chat_id=callback.from_user.id, message_id=msg_id)

        await callback.answer()
        await callback.message.answer(
            text=cfg.misc.texts.messages.success_msg.format(href),
            reply_markup=delete_markup
        )
    else:
        await callback.answer()

        for msg_id in delete_ids:
            await callback.bot.delete_message(chat_id=callback.from_user.id, message_id=msg_id)


async def revoke_ad(callback: CallbackQuery, callback_data: dict):
    mw_data = ctx_data.get()
    cfg: Config = mw_data['config']
    repo: Repo = mw_data['repo']

    ad_id = callback_data.get("ad_id")
    msg_ids_str: str = callback_data.get("msg_ids")
    msg_ids = msg_ids_str.split(",")

    for msg_id in msg_ids:
        await callback.bot.delete_message(
            chat_id=cfg.tg_bot.channel_id,
            message_id=int(msg_id)
        )
    await repo.revoke_ad(ad_id)

    await callback.message.edit_text(text=cfg.misc.texts.messages.revoked_msg)


def register_user(dp: Dispatcher, cfg: Config):
    rent_btn_text = cfg.misc.texts.buttons.rent
    sell_btn_text = cfg.misc.texts.buttons.sell
    dp.register_message_handler(user_start, commands=["start"], state="*")

    dp.register_message_handler(sell_command, regexp=sell_btn_text, state="*")
    dp.register_message_handler(user_start, commands=["sell"], state="*")

    dp.register_message_handler(rent_command, regexp=rent_btn_text, state="*")
    dp.register_message_handler(user_start, commands=["rent"], state="*")

    dp.register_callback_query_handler(show_photo, get_photo_cd.filter(), state="*")
    dp.register_callback_query_handler(delete_photo, delete_photo_cd.filter(), state="*")

    dp.register_callback_query_handler(category_navigate, ad_cd.filter(), state="*")
    dp.register_callback_query_handler(change_photo, photo_cd.filter(), state="*")
    dp.register_callback_query_handler(change_description, desc_cd.filter(), state="*")
    dp.register_callback_query_handler(change_cost, cost_cd.filter(), state="*")
    dp.register_callback_query_handler(publish_ad, publish_cd.filter(), state="*")
    dp.register_callback_query_handler(confirm_ad, confirm_publish_cd.filter(), state="confirm_ad")
    dp.register_callback_query_handler(revoke_ad, revoke_cd.filter(), state="*")

    dp.register_message_handler(wait_description, state="wait_description")
    dp.register_message_handler(wait_cost, state="wait_cost")

    dp.register_callback_query_handler(change_new_cost, new_cost_cd.filter(), state="*")

    dp.register_message_handler(wait_new_description, state="wait_new_description")
    dp.register_message_handler(wait_new_cost, state="wait_new_cost")
    dp.register_message_handler(wait_new_photo, state="wait_new_photo", content_types=["photo"])

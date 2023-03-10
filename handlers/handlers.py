import time
from typing import List

from aiogram import types
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import Message, InputMedia
from aiogram_dialog import DialogManager, StartMode

from handlers.dialog import MySG, PostMessage, AdminMessage, bot, dp

from throttling import rate_limit

from config import load_config

config = load_config('.env')


@rate_limit(5, key='start')
async def cmd_start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MySG.main, mode=StartMode.RESET_STACK)


async def load_text(message: types.Message, dialog_manager: DialogManager):
    PostMessage.caption_text = f'{message.text}\n\n{message.from_user.first_name} {message.from_user.last_name}'
    if message.from_user.username:
        PostMessage.caption_text = PostMessage.caption_text + f'\n@{message.from_user.username}'
    await message.answer(f'Ваш текст предложенной новости выглядит так:\n\n\n↓ ↓ ↓')
    time.sleep(3)
    await message.answer(PostMessage.caption_text)
    time.sleep(3)
    await dialog_manager.start(MySG.choose1)
    await MySG.main.set()


async def send_media(message: types.Message, dialog_manager: DialogManager, album: List[types.Message]):
    media_group = types.MediaGroup()
    for obj in album:
        if obj.photo:
            file_id = obj.photo[-1].file_id
        else:
            file_id = obj[obj.content_type].file_id
        try:
            if obj == album[0]:
                media_group.attach(InputMedia(media=file_id,
                                              type=obj.content_type,
                                              caption=PostMessage.caption_text))
            else:
                media_group.attach(InputMedia(media=file_id, type=obj.content_type))
        except ValueError:
            return await message.answer("This type of album is not supported by aiogram.")
    PostMessage.media_list = media_group
    await message.answer("Ваш пост будет опубликован в таком виде:")
    time.sleep(2)
    await message.answer_media_group(PostMessage.media_list)
    time.sleep(3)
    await dialog_manager.start(MySG.choose2)
    await MySG.main.set()


async def send_only_one_mediafile(message: types.Message, dialog_manager: DialogManager):
    media_group = types.MediaGroup()
    type_att = message.content_type
    if type_att == 'photo':
        file_id = message.photo[-1].file_id
    else:
        file_id = message[type_att].file_id
    media_group.attach(InputMedia(media=file_id,
                                  type=type_att,
                                  caption=PostMessage.caption_text))
    PostMessage.media_list = media_group
    await message.answer("Ваш пост будет опубликован в таком виде:")
    time.sleep(2)
    await message.answer_media_group(media_group)
    time.sleep(2)
    await dialog_manager.start(MySG.choose2)
    await MySG.main.set()


async def load_admin_text(message: types.Message, dialog_manager: DialogManager):
    text = f"---Сообщение Админу---" \
           f"Отправитель:\n" \
           f"{message.from_user.id}\n" \
           f"@{message.from_user.username}\n" \
           f"{message.from_user.first_name} {message.from_user.last_name}\n" \
           f"Сообщение:\n" \
           f" - - - {message.text}"
    await bot.send_message(chat_id=config.tg_bot.admin_id,
                           text=text)
    await message.reply('Сообщение админу отправлено, он уже читает его')
    time.sleep(10)
    await MySG.main.set()
    await dialog_manager.start(MySG.main, mode=StartMode.RESET_STACK)


def register_all_handlers():
    dp.register_message_handler(cmd_start, CommandStart())
    dp.register_message_handler(load_text, state=PostMessage.caption)
    dp.register_message_handler(send_media, state=PostMessage.media, is_media_group=True,
                                content_types=types.ContentType.ANY)
    dp.register_message_handler(send_only_one_mediafile, state=PostMessage.media, content_types=types.ContentType.ANY)
    dp.register_message_handler(load_admin_text, state=AdminMessage.text)

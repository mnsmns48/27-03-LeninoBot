import asyncio
import logging
import time
from typing import Union, List

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import CallbackQuery, Message, InputMedia
from aiogram_dialog import DialogRegistry, DialogManager, Window, Dialog, StartMode
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Const, Format

from config import load_config

from aiogram import Bot, Dispatcher, executor, types

config = load_config('.env')
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.tg_bot.bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())

registry = DialogRegistry(dp)


class MySG(StatesGroup):
    main = State()
    choose1 = State()
    choose2 = State()


class AdminMessage(StatesGroup):
    str_text = str()
    text = State()


class PostMessage(StatesGroup):
    caption_text = str()
    media_list = types.MediaGroup()
    caption = State()
    media = State()


class AlbumMiddleware(BaseMiddleware):
    album_data: dict = {}

    def __init__(self, latency: Union[int, float] = 0.02):
        self.latency = latency
        super().__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        if not message.media_group_id:
            return
        try:
            self.album_data[message.media_group_id].append(message)
            raise CancelHandler()
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)

            message.conf["is_last"] = True
            data["album"] = self.album_data[message.media_group_id]

    async def on_post_process_message(self, message: types.Message, result: dict, data: dict):
        if message.media_group_id and message.conf.get("is_last"):
            del self.album_data[message.media_group_id]


async def go_post(c: CallbackQuery, button: Button, manager: DialogManager):
    await PostMessage.caption.set()
    await c.message.answer("Введите текст новости и нажмите -ОТПРАВИТЬ-")


async def go_admin(c: CallbackQuery, button: Button, manager: DialogManager):
    await AdminMessage.text.set()
    await c.message.answer("Пишите, отправляйте, админ всегда на связи")


async def send_only_text(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await bot.send_message(chat_id=config.tg_bot.admin_id,
                           text="---Предложен пост---")
    time.sleep(1)
    await bot.send_message(chat_id=config.tg_bot.admin_id,
                           text=f'{PostMessage.caption_text}')
    await c.message.answer("Новость предложена")
    time.sleep(10)
    await dialog_manager.start(MySG.main, mode=StartMode.RESET_STACK)


async def finish_post(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await bot.send_message(chat_id=config.tg_bot.admin_id,
                           text="---Предложен пост---")
    time.sleep(1)
    await bot.send_media_group(chat_id=config.tg_bot.admin_id, media=PostMessage.media_list)
    await c.message.answer("Новость предложена")
    time.sleep(10)
    await dialog_manager.start(MySG.main, mode=StartMode.RESET_STACK)


async def add_media(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await PostMessage.media.set()
    await c.message.answer("Добавьте медиафайлы\n\nМожно несколько фото или видео")


async def cancel(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await c.message.answer("Отменяем. Нужно начинать заново")
    await dialog_manager.start(MySG.main, mode=StartMode.RESET_STACK)


@dp.message_handler(CommandStart())
async def cmd_start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MySG.main, mode=StartMode.RESET_STACK)


@dp.message_handler(state=PostMessage.caption)
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


@dp.message_handler(state=PostMessage.media, is_media_group=True, content_types=types.ContentType.ANY)
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


@dp.message_handler(state=PostMessage.media, content_types=types.ContentType.ANY)
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


@dp.message_handler(state=AdminMessage.text)
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



row1 = Row(
    Button(Const("Предложить пост"), id="post", on_click=go_post),
    Button(Const("Написать админу"), id="admin_message", on_click=go_admin),

)

row2 = Row(
    Button(Const("+ Медиа"), id="send", on_click=add_media),
    Button(Const("Без Медиа"), id="send_only_text", on_click=send_only_text),

)
row3 = Row(
    Button(Const("Да"), id="finish_post", on_click=finish_post),
    Button(Const("Отмена"), id="cancel", on_click=cancel),

)

main_window = Dialog(
    Window(
        Format(f"Получаем предложения по новостям в @leninocremia\n\n"
               f"/start - начало работы бота\n"
               f"/help - поможет разобраться\n\n"
               f"Тут всё просто:\n\n          ↓ ↓ ↓                              ↓ ↓ ↓"),
        row1,
        state=MySG.main,
    ),
    Window(
        Format("↑ ↑ ↑\n\n\nОтправляем в таком виде? или добавим медиа файлы"),
        row2,
        state=MySG.choose1,
    ),
    Window(
        Format("Публикуем в @leninocremia ?\n\nПост можно предложить не чаще одного раза в час"),
        row3,
        state=MySG.choose2,
    ),
)

registry.register(main_window)

if __name__ == '__main__':
    dp.middleware.setup(AlbumMiddleware())
    executor.start_polling(dp, skip_updates=True)

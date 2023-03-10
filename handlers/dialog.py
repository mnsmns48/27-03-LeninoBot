import time

from aiogram import types, Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogRegistry, DialogManager, Window, Dialog, StartMode

from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Const, Format

from config import load_config

config = load_config('.env')

bot = Bot(token=config.tg_bot.bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())


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

registry = DialogRegistry(dp)


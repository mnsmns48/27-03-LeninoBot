import operator
from typing import Any

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, ParseMode, CallbackQuery, ContentType

from aiogram_dialog import Window, Dialog, DialogRegistry, DialogManager, StartMode, ChatEvent
from aiogram_dialog.widgets.kbd import Button, Row, Column, Group, Checkbox, ManagedCheckboxAdapter, Select, Radio, \
    Multiselect
from aiogram_dialog.widgets.media import StaticMedia

from aiogram_dialog.widgets.text import Const, Format

from config import load_config

config = load_config('../.env')

storage = MemoryStorage()
bot = Bot(token=config.tg_bot.bot_token)
dp = Dispatcher(bot, storage=storage)
registry = DialogRegistry(dp)


class DialogSG(StatesGroup):
    greeting = State()


windows = Window(
    StaticMedia(
        path='/Users/smdlkhn/PycharmProjects/27-03-LeninoBot/v773rxoVRsk.jpeg',
        type=ContentType.PHOTO,
    ),
    state=DialogSG.greeting,
)

dialog = Dialog(windows)
registry.register(dialog)


@dp.message_handler(commands=["start"])
async def start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(DialogSG.greeting, mode=StartMode.RESET_STACK)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

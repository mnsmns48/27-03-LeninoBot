from typing import Dict

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, ContentType, message
from aiogram_dialog import Window, Dialog, DialogRegistry, DialogManager, StartMode, ChatEvent
from aiogram_dialog.widgets.kbd import Group, Row, Button
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Multi, Const, Format
from aiogram_dialog.widgets.when import Whenable

from config import load_config

config = load_config('../.env')

storage = MemoryStorage()
bot = Bot(token=config.tg_bot.bot_token)
dp = Dispatcher(bot, storage=storage)
registry = DialogRegistry(dp)


class MySG(StatesGroup):
    main = State()


async def get_data(**kwargs):
    return {
        "name": "W P",
        "extended": True,
    }


def tser(data: Dict, widget: Whenable, manager: DialogManager):
    return data.get("name") == "W P"


window = Window(
    Multi(
        Const("Hello"),
        Format("{name}", when="extended"),
        sep=" ",
    ),
    Group(
        Row(
            Button(Const("Wait"), id="wait"),
            Button(Const("Ignore"), id="ignore"),
            when="extended",
        ),
        Button(Const("Admin mode"), id="nothing", when=tser),
    ),
    state=MySG.main,
    getter=get_data,
)

dialog = Dialog(window)
registry.register(dialog)


@dp.message_handler(commands=['start'])
async def start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MySG.main, mode=StartMode.RESET_STACK)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

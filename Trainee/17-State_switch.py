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

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery

from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Const
from config import load_config

config = load_config('../.env')

storage = MemoryStorage()
bot = Bot(token=config.tg_bot.bot_token)
dp = Dispatcher(bot, storage=storage)
registry = DialogRegistry(dp)


class DialogSG(StatesGroup):
    first = State()
    second = State()
    third = State()


async def to_second(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(DialogSG.second)


async def go_back(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().back()


async def go_next(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().next()


wind = Dialog(
        Window(
            Const("First"),
            Button(Const("To second"), id="sec", on_click=to_second),
            state=DialogSG.first,
        ),
        Window(
            Const("Second"),
            Row(
                Button(Const("Back"), id="back2", on_click=go_back),
                Button(Const("Next"), id="next2", on_click=go_next),
            ),
            state=DialogSG.second,
        ),
        Window(
            Const("Third"),
            Button(Const("Back"), id="back3", on_click=go_back),
            state=DialogSG.third,
        )
    )


registry.register(wind)


@dp.message_handler(commands=['start'])
async def start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(DialogSG.first, mode=StartMode.RESET_STACK)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
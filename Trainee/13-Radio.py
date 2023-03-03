import operator
from typing import Any

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, ParseMode, CallbackQuery

from aiogram_dialog import Window, Dialog, DialogRegistry, DialogManager, StartMode, ChatEvent
from aiogram_dialog.widgets.kbd import Button, Row, Column, Group, Checkbox, ManagedCheckboxAdapter, Select, Radio

from aiogram_dialog.widgets.text import Const, Format

from config import load_config

config = load_config('../.env')

storage = MemoryStorage()
bot = Bot(token=config.tg_bot.bot_token)
dp = Dispatcher(bot, storage=storage)
registry = DialogRegistry(dp)


class MySG(StatesGroup):
    main = State()


async def get_data(**kwargs):
    fruits = [
        ("Apple", '1'),
        ("Pear", '2'),
        ("Orange", '3'),
        ("Banana", '4'),
    ]
    return {
        "fruits": fruits,
        "count": len(fruits),
    }


async def on_fruit_selected(c: CallbackQuery, widget: Any, manager: DialogManager, item_id: str):
    print("Fruit selected: ", item_id)


fruits_kbd = Radio(
    Format("🔘 {item[0]}"),  # E.g `🔘 Apple`
    Format("⚪️ {item[0]}"),
    id="r_fruits",
    item_id_getter=operator.itemgetter(1),
    items="fruits",
    on_click=on_fruit_selected,
)


main_window = Window(
    Const("Hello!"),
    fruits_kbd,
    state=MySG.main,
    getter=get_data,
)


dialog = Dialog(main_window)
registry.register(dialog)


@dp.message_handler(commands=["start"])
async def start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MySG.main, mode=StartMode.RESET_STACK)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

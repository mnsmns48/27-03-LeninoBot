from typing import Dict

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message

from aiogram_dialog import Window, Dialog, DialogRegistry, DialogManager, StartMode

from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format, Multi, Case

from config import load_config

config = load_config('../.env')

storage = MemoryStorage()
bot = Bot(token=config.tg_bot.bot_token)
dp = Dispatcher(bot, storage=storage)
registry = DialogRegistry(dp)


class MySG(StatesGroup):
    main = State()


async def get_data(**kwargs):
    return {"color": "green", "number": 41}


text = Case(
    {
        "red": Const("Square"),
        "green": Const("Unicorn"),
        "blue": Const("Moon"),
    },
    selector="color",
)


def parity_selector(data: Dict, case: Case, manager: DialogManager):
    return data["number"] % 2


text2 = Case(
    {
        0: Format("{number} is even!"),
        1: Const("It is Odd"),
    },
    selector=parity_selector,
)

dialog = Dialog(
    Window(
        text,
        text2,
        Button(Const("Это просто кнопка"), id="nothing"),
        state=MySG.main,
        getter=get_data,  # here we set our data getter
    )
)

registry.register(dialog)


@dp.message_handler(commands=["start"])
async def start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MySG.main, mode=StartMode.RESET_STACK)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

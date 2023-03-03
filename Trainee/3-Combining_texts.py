from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message

from aiogram_dialog import Window, Dialog, DialogRegistry, DialogManager, StartMode

from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format, Multi

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
        "name": "Геша",
        "surname": "Гошинский"
    }


text = Multi(
    Const("Hello!"),
    Const("And goodbye!"),
    sep=" ",
)

text2 = Multi(
    Format("Hello, {name}"),
    Const("and goodbye {name}!"),
    sep=", ",
)

text3 = Multi(
    Multi(Const("01"), Const("02"), Const("2003"), sep="."),
    Multi(Const("04"), Const("05"), Const("06"), sep=":"),
    sep="T"
)

dialog = Dialog(
    Window(
        text3,
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

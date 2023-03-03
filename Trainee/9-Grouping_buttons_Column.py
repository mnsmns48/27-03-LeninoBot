from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, ParseMode, CallbackQuery

from aiogram_dialog import Window, Dialog, DialogRegistry, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, Row, Column

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
    return {
        "name": "Геша"
    }


async def fly_clicked(c: CallbackQuery, button: Button, manager: DialogManager):
    await c.message.answer("Вот ты и научился!")


async def go_clicked(c: CallbackQuery, button: Button, manager: DialogManager):
    await c.message.answer("Going on!")


async def run_clicked(c: CallbackQuery, button: Button, manager: DialogManager):
    await c.message.answer("Running!")


async def fly_clicked(c: CallbackQuery, button: Button, manager: DialogManager):
    await c.message.answer("Вот ты и научился!")


column = Column(
    Button(Const("Go"), id="go", on_click=go_clicked),
    Button(Const("Run"), id="run", on_click=run_clicked),
    Button(Const("Fly"), id="fly", on_click=fly_clicked),
)

main_window = Window(
    Format("Hello, {name}!"),
    column,
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

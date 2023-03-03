from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, ParseMode, CallbackQuery

from aiogram_dialog import Window, Dialog, DialogRegistry, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from aiogram_dialog.widgets.text import Const, Format, Multi, Case, Jinja

from config import load_config

config = load_config('../.env')

storage = MemoryStorage()
bot = Bot(token=config.tg_bot.bot_token)
dp = Dispatcher(bot, storage=storage)
registry = DialogRegistry(dp)


class MySG(StatesGroup):
    main = State()


async def go_clicked(c: CallbackQuery, button: Button, manager: DialogManager):
    await c.message.answer("Going on!")


go_btn = Button(
    Const("Go"),
    id="go",  # id is used to detect which button is clicked
    on_click=go_clicked,

)

main_window = Window(
    Const("Hello, unknown person"),
    go_btn,
    state=MySG.main,
)

dialog = Dialog(main_window)
registry.register(dialog)


@dp.message_handler(commands=["start"])
async def start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MySG.main, mode=StartMode.RESET_STACK)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

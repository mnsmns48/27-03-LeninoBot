from aiogram_dialog.tools import render_transitions

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils import executor

from aiogram_dialog import Dialog, Window, DialogRegistry, DialogManager, StartMode

from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Row, SwitchTo, Next, Back
from aiogram_dialog.widgets.text import Const
from config import load_config

config = load_config('../.env')

storage = MemoryStorage()
bot = Bot(token=config.tg_bot.bot_token)
dp = Dispatcher(bot, storage=storage)
registry = DialogRegistry(dp)


class RenderSG(StatesGroup):
    first = State()
    second = State()
    third = State()


async def on_input(m: Message, dialog: Dialog, manager: DialogManager):
    manager.current_context().dialog_data["name"] = m.text
    await dialog.next()


dialog = Dialog(
    Window(
        Const("1. First"),
        Next(),
        state=RenderSG.first,
    ),
    Window(
        Const("2. Second"),
        Row(
            Back(),
            Next(),
        ),
        MessageInput(on_input),
        state=RenderSG.second,
    ),
    Window(
        Const("3. Last"),
        Back(),
        state=RenderSG.third,
    ),
)

render_transitions([dialog])

# registry.register(wind)


@dp.message_handler(commands=['start'])
async def start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(RenderSG.first, mode=StartMode.RESET_STACK)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils import executor

from aiogram_dialog import Dialog, Window, DialogRegistry, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Row, SwitchTo, Next, Back
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


wind = Dialog(
    Window(
        Const("First"),
        SwitchTo(Const("To second"), id="sec", state=DialogSG.second),
        state=DialogSG.first,
    ),
    Window(
        Const("Second"),
        Row(
            Back(),
            Next(),
        ),
        state=DialogSG.second,
    ),
    Window(
        Const("Third"),
        Back(),
        state=DialogSG.third,
    )
)


registry.register(wind)


@dp.message_handler(commands=['start'])
async def start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(DialogSG.first, mode=StartMode.RESET_STACK)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
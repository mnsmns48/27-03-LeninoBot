from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, ParseMode

from aiogram_dialog import Window, Dialog, DialogRegistry, DialogManager, StartMode

from aiogram_dialog.widgets.text import Const, Format, Multi, Case, Jinja

from config import load_config

config = load_config('../.env')

storage = MemoryStorage()
bot = Bot(token=config.tg_bot.bot_token)
dp = Dispatcher(bot, storage=storage)
registry = DialogRegistry(dp)


class DialogSG(StatesGroup):
    ANIMALS = State()


async def get_data(**kwargs):
    return {
        "title": "Animals list",
        "animals": ["cat", "dog", "my brother's tortoise"]
    }


html_text = Jinja("""
<b>{{title}}</b>
{% for animal in animals %}
* <a href="https://yandex.ru/search/?text={{ animal }}">{{ animal|capitalize }}</a>
{% endfor %}
""")

window = Window(
    html_text,
    parse_mode=ParseMode.HTML,  # do not forget to set parse mode
    state=DialogSG.ANIMALS,
    getter=get_data
)

dialog = Dialog(window)
registry.register(dialog)


@dp.message_handler(commands=["start"])
async def start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(DialogSG.ANIMALS, mode=StartMode.RESET_STACK)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

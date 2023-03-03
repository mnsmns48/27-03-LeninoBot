import logging

from config import load_config

from aiogram import Bot, Dispatcher, executor, types

config = load_config('.env')
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.tg_bot.bot_token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.answer(f"{message.from_user.first_name} {message.from_user.last_name},\nСкоро всё будет...")


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(f"На любое сообщение я отвечаю пока так\n доступные команды: \n/start\n/help")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

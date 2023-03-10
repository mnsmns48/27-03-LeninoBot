import logging

from handlers.dialog import dp, registry, main_window
from handlers.handlers import register_all_handlers
from middleware.Throttling import ThrottlingMiddleware
from middleware.AlbumMiddleware import AlbumMiddleware
from config import load_config

from aiogram import executor

config = load_config('.env')
logging.basicConfig(level=logging.INFO,
                    format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s', )


def register_all_middlewares():
    dp.middleware.setup(ThrottlingMiddleware())
    dp.middleware.setup(AlbumMiddleware())


if __name__ == '__main__':
    register_all_middlewares()
    register_all_handlers()
    registry.register(main_window)
    executor.start_polling(dp, skip_updates=True)

import logging

from aiogram.utils import executor

from database import db
import aiobot

logging.basicConfig(level=logging.INFO)


async def on_startup(*args, **kwargs):
    db.init()
    await db.drop_all()
    await db.create_all()


if __name__ == '__main__':
    executor.start_polling(aiobot.dis, on_startup=on_startup, skip_updates=True)

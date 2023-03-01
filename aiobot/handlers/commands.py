from aiogram.types import Message

from aiobot.models import User
from aiobot.dispatcher import dis


@dis.message_handler(commands=['start'])
async def send_welcome(msg: Message):
    user_id = str(msg.from_user.id)
    if not await User.get(user_id):
        data = {
            'full_name': msg.from_user.full_name,
        }
        await User.create(user_id, **data)
        await msg.answer('Created')
    await msg.answer('Exists')

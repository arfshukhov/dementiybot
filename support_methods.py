import logging
import json
from pathlib import Path
import os
import subprocess
import emoji
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ContentType, Message, File
from db_ops import *


API_TOKEN = '5531261630:AAEhBlU9fwMZeNf47nYZbUjb95MeVl3zYaE'


# logging.basicConfig(level=logging.DEBUG)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


async def switch_types(message, file_id, type: str, phrase):

    new_bind = add_new_bind(
        chat_id=message.chat.id,
        type=type,
        phrase=phrase,
        answer=file_id)
    await message.reply(new_bind)


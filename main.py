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

#'5558759642:AAEBYYZzgJv4GPT8YMzf6qgAh14klSKowtY'
# Configure logging

logging.basicConfig(level=logging.DEBUG)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


async def switch_types(end_path: str, message, phrase, type: str, expansion: str, limit: int, limit_text: str):
    path = os.getcwd() + end_path
    file = await message.reply_to_message.animation.get_file()
    file_name = "".join([str(message.chat.id), "_", f"{type}", "_", str(phrase), expansion])

    new_bind = add_new_bind(
        chat_id=message.chat.id,
        type=type,
        phrase=phrase,
        answer=file_name)

    await bot.download_file(file_path=file.file_path, destination=f"{path}{file_name}")

    if os.stat(f"{path}{file_name}").st_size > limit:  # 5_242_880
        os.remove(f"{path}{file_name}")
        await message.reply(f"Файл слишком большой (макс. для {limit_text})")

    elif os.stat(f"{path}{file_name}").st_size <= limit:
        await message.reply(new_bind)


@dp.message_handler(commands=['help_demy'])
async def send_welcome(message: types.Message):
    await message.reply("Привет, я админ-бот Дементий от @Harfile" "\n"
                        '/bind ("ваша фраза") - можно добавить бинд, который будет срабатывать на определенное слово'
                        'или фразу. Чтобы воспользоваться функцией, нужно после команды, отстпив пробел, написать в'
                        'скобках и ковычках фразу-триггер. Триггер можно снять командой /unbind аналогичным образом.'
                        'Сейчас доступны следующие типы триггеров: текст, видео, голосовые сообщения, видео, фото, gif'
                        'и стикеры.\n'
                        '/echo - отправитель сообщения закукарекает.\n'
                        '/dice - бросает кость, через пробел можно указать число бросков, но не более 10.\n'
                        '/ban и /unban - в ответ на сообщение банит пользователя')


@dp.message_handler(commands=['echo'])
async def echooo(message):
    msg = str(message.reply_to_message.text)
    print("\n\n\n", msg, "\n\n\n")
    await message.reply(f"Петух по имени {message.reply_to_message.from_user.mention} кукарекнул: {msg}")


@dp.message_handler(commands=["dice"])
async def dice(message):
    times = str(message.text).removeprefix('/dice ')
    if times.isdecimal():
        if int(times) <= 10:
            for _ in range(int(times)):
                await bot.send_dice(message.chat.id, None, None, "\U0001F3B2")
        else:
            await message.answer("В качестве аргумента числа не больше 10")
    else:
        await bot.send_dice(message.chat.id, None, None, "\U0001F3B2")


@dp.message_handler(content_types=[ContentType.NEW_CHAT_MEMBERS])
async def new_members_handler(message: Message):
    new_member = message.new_chat_members[0]
    await bot.send_message(message.chat.id, f"Добро пожаловать, {new_member.mention}")


@dp.message_handler(commands=["ban"], is_chat_admin=True)
async def ban(message):
    member = str(message.text).removeprefix('/ban')
    admin_rights = await message.chat.get_member(message.from_user.id)
    print(admin_rights, " \n", message.reply_to_message.from_user.id)
    dump = json.dumps(dict(admin_rights))

    if '"can_restrict_members": true' in dump:
        try:
            await bot.kick_chat_member(chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id)  #
            await bot.send_message(message.chat.id,
                                   f"Пользователь {message.reply_to_message.from_user.mention} забанен")
        except:
            await message.reply(f"Я не могу его забанить {message.reply_to_message.from_user.mention}")
    else:
        await bot.send_message(message.chat.id, "хуй соси, говно написал")


@dp.message_handler(commands=["unban"], is_chat_admin=True)
async def unban(message):
    admin_rights = await message.chat.get_member(message.from_user.id)
    dump = json.dumps(dict(admin_rights))
    if '"can_restrict_members": true' in dump:
        try:
            await message.bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            await bot.send_message(message.chat.id, "Пользователь разбанен")
        except:
            await bot.send_message(message.chat.id, "Что-то пошло не так, разбаньте пользователя вручную")
    else:
        await bot.send_message(message.chat.id, " ")


@dp.message_handler(commands=["bind"])
async def set_bind(message):
    if message.text[6] == "(" and message.text[-1] == ")":
        msg = message.text[8:-2:1]
        if not msg.isspace():

            match message.reply_to_message.content_type:

                case "text":
                    new_bind = add_new_bind(
                        chat_id=message.chat.id,
                        type="text",
                        phrase=msg,
                        answer=message.reply_to_message.text)
                    await message.reply(new_bind)

                case "voice":
                    await switch_types(end_path=r"\\animation\\",
                                       message=message,
                                       phrase=msg,
                                       type="animation",
                                       expansion=".gif",
                                       limit=7_340_032,
                                       limit_text="GIF 7 МБ")

                case "animation":  # 15_728_640
                    await switch_types(end_path=r"\\animation\\",
                                       message=message,
                                       phrase=msg,
                                       type="animation",
                                       expansion=".gif",
                                       limit=7_340_032,
                                       limit_text="GIF 7 МБ")

                case "photo":
                    await switch_types(end_path=r"\\photo\\",
                                       message=message,
                                       phrase=msg,
                                       type="photo",
                                       expansion=".jpg",
                                       limit=5_242_880,
                                       limit_text="фото 5 МБ")
                case "sticker":
                    new_bind = add_new_bind(
                        chat_id=message.chat.id,
                        type="sticker",
                        phrase=msg,
                        answer=message.reply_to_message.sticker.file_id)
                    await message.reply(new_bind)
                case _:
                    await message.reply("Биндов такого типа пока не завезли)")

        else:
            await message.reply("Что биндить-то?")
    else:
        await message.reply('Ваш бинд имеет неверный вид.\n'
                            'Бинд должен иметь следующий вид: /bind ("ваша фраза")\n'
                            'т.е. аргументы для команды передаются в скобках и ковычках, с отступом в один пробел от самоый команды.')


@dp.message_handler(commands=["unbind"])
async def remove_bind(message):
    if message.text[8] == "(" and message.text[-1] == ")":
        msg = message.text[10:-2:1]
        rem_bind = remove_binds(
            id=message.chat.id,
            phras=msg)
        await message.reply(rem_bind)
    else:
        await message.reply('Ваша команда имеет неверный вид.\n'
                            'Unbind должен иметь следующий вид: /unbind ("ваша фраза")\n'
                            'т.е. аргументы для команды передаются в скобках и ковычках, с отступом в один пробел от самоый команды.')


@dp.message_handler(content_types=['text'])
async def filter_messages(message: types.Message):
    bind = await get_binds(chat_id=int(message.chat.id))
    for elem in bind:
        if elem[1] in message.text.lower():
            match elem[0]:

                case "text":
                    await message.reply(str(elem[2]))

                case "voice":
                    path = os.getcwd() + r"\\audio\\"
                    with open(f"{path}{str(elem[2])}", "rb") as file:
                        await message.reply_voice(file)

                case "video":
                    path = os.getcwd() + r"\\video\\"
                    with open(f"{path}{str(elem[2])}", "rb") as file:
                        await message.reply_video(file)

                case "animation":
                    path = os.getcwd() + r"\\animation\\"
                    with open(f"{path}{str(elem[2])}", "rb") as file:
                        await message.reply_animation(file)

                case "photo":
                    path = os.getcwd() + r"\\photo\\"
                    with open(f"{path}{str(elem[2])}", "rb") as file:
                        await message.reply_animation(file)

                case "sticker":
                    await message.reply_sticker(str(elem[2]))

                case _:
                    await bot.send_message(message.chat.id, "error")


if __name__ == '__main__':
    executor.start_polling(dp)

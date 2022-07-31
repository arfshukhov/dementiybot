import logging

import json

from pathlib import Path

import os

import subprocess

import emoji

from aiogram import Bot, Dispatcher, executor, types

from aiogram.types import ContentType, Message, File

from db_ops import *

API_TOKEN = '5558759642:AAEBYYZzgJv4GPT8YMzf6qgAh14klSKowtY'

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


#async def handle_file(file: File, file_name: str, path: str):
    #Path(f"{path}").mkdir(parents=True, exist_ok=True)





@dp.message_handler(commands=['help_eugen'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Привет, я админ-бот Prinz Eugen от @Harfile" "\n"
                        "Ща допишу, здесь все доступные команды будут...")


@dp.message_handler(commands=['echo'])
async def echooo(message):
    msg = str(message.text).removeprefix('/echo')
    print("\n\n\n", msg, "\n\n\n")
    await message.reply(f"Петух по имени {message.from_user.mention} кукарекнул: {msg}")


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
                    path = os.getcwd()+r"\\audio\\"
                    voice = await message.reply_to_message.voice.get_file()
                    file_name = "".join([str(message.chat.id), "_", "audio", "_", str(msg), ".ogg"])

                    new_bind = add_new_bind(
                        chat_id=message.chat.id,
                        type="voice",
                        phrase=msg,
                        answer=file_name)

                    await bot.download_file(file_path=voice.file_path, destination=f"{path}{file_name}")
                    await message.reply(new_bind)

                case "video":
                    path = os.getcwd() + r"\\video\\"
                    video = await message.reply_to_message.video.get_file()
                    file_name = "".join([str(message.chat.id), "_", "video", "_", str(msg), ".mp4"])

                    new_bind = add_new_bind(
                        chat_id=message.chat.id,
                        type="video",
                        phrase=msg,
                        answer=file_name)

                    await bot.download_file(file_path=video.file_path, destination=f"{path}{file_name}")

                    if os.stat(f"{path}{file_name}").st_size > 15_728_640:#52_428_000
                        os.remove(f"{path}{file_name}")
                        await message.reply("Файл слишком большой (пока что, макс. для видео: 15 МБ).\n" 
                                            "Вы можете попробовать сжать файл при отправке.")

                    elif os.stat(f"{path}{file_name}").st_size <= 15_728_640:#52_428_000
                        await message.reply(new_bind)

                case "animation":
                    path = os.getcwd() + r"\\animation\\"
                    animation = await message.reply_to_message.animation.get_file()
                    file_name = "".join([str(message.chat.id), "_", "animation", "_", str(msg), ".gif"])

                    await message.reply(os.path.getsize(animation))

                    new_bind = add_new_bind(
                        chat_id=message.chat.id,
                        type="animation",
                        phrase=msg,
                        answer=file_name)

                    await bot.download_file(file_path=animation.file_path, destination=f"{path}{file_name}")

                    if os.stat(f"{path}{file_name}").st_size > 7_340_032:
                        os.remove(f"{path}{file_name}")
                        await message.reply("Файл слишком большой (макс. для GIF 7 МБ)")

                    elif os.stat(f"{path}{file_name}").st_size <= 7_340_032:
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
    rem_bind = remove_binds(
        chat_id=message.chat.id,
        phrase=message.text
    )
    pass


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
                    file = open(f"{path}{str(elem[2])}", "rb")
                    await message.reply_voice(file)
                    file.close()

                case "video":
                    path = os.getcwd() + r"\\video\\"
                    file = open(f"{path}{str(elem[2])}", "rb")
                    await message.reply_video(file)
                    file.close()

                case "animation":
                    path = os.getcwd() + r"\\animation\\"
                    file = open(f"{path}{str(elem[2])}", "rb")
                    await message.reply_animation(file)
                    file.close()

                case _:
                    await bot.send_message(message.chat.id, "error")


if __name__ == '__main__':
    executor.start_polling(dp)

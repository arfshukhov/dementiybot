"""
 2This is a echo bot.
 3It echoes any incoming text messages.
 4"""

import logging

import json

import emoji

from aiogram import Bot, Dispatcher, executor, types

from aiogram.types import ContentType, Message

API_TOKEN = '5558759642:AAEBYYZzgJv4GPT8YMzf6qgAh14klSKowtY'

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


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

    #await bot.send_message(message.chat.id, "\n".join([str(admin_rights), "\n",
    #                                                   str(message.reply_to_message.from_user.id), "\n",
    #                                                   dump]))
    if '"can_restrict_members": true' in dump:
        try:
            await bot.kick_chat_member(chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id)
            await bot.send_message(message.chat.id, "Пользователь забанен")

        except:
            await bot.send_message(message.chat.id, "Я не могу его забанить")
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
        await bot.send_message(message.chat.id, "хуй соси, говно написал")


@dp.message_handler()
async def filter_messages(message):
    if "украина" in str(message.text).lower():
        await message.reply("УГИЛ, ес че")


if __name__ == '__main__':
    executor.start_polling(dp)
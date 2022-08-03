from support_methods import *

import logging
import json
from pathlib import Path
import os
import subprocess
import emoji
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ContentType, Message, File
from db_ops import *


@dp.message_handler(commands=['help_demy', "help"])
async def send_welcome(message: types.Message):
    await message.reply("Привет, я админ-бот Дементий от @Harfile\n"
                        '/bind ("ваша фраза") - можно добавить бинд, который будет срабатывать на определенное слово'
                        'или фразу. Чтобы воспользоваться функцией, нужно после команды, отстпив пробел, написать в'
                        'скобках и ковычках фразу-триггер. \nТриггер можно снять командой /unbind, команда имеет '
                        'аналогичный с /bind синтаксис.\n' 
                        'Сейчас доступны следующие типы триггеров: текст, видео, голосовые сообщения, видео, фото, gif'
                        'и стикеры.\n'
                        '/echo - отправитель сообщения закукарекает.\n'
                        '/dice - бросает кость, через пробел можно указать число бросков, но не более 10.\n'
                        '/wiki_get ("название статьи") команда возвращает статью на Википедии.\n'
                        '/ban и /unban - в ответ на сообщение банит пользователя\n'
                        '/mobilize - мобилизует пользователя'
                        '/report - отправить репорт разработчику, будь то жалоба или предложение. после слова /report '
                        'оставьте текст')


@dp.message_handler(commands=['echo'])
async def echo(message):
    if message.reply_to_message:
        msg = str(message.reply_to_message.text)
        await message.reply(f"Петух по имени {message.reply_to_message.from_user.mention} кукарекнул: {msg}")


@dp.message_handler(commands=["mobilize"])
async def mobilize(message):
    print(message.from_user.id)
    with open("templates/mobilize.jpg", 'rb') as pht:
        await message.reply_to_message.reply_photo(pht)


@dp.message_handler(commands=["report"])
async def send_report(message):
    report = "\n".join([message.from_user.mention, str(message.text).removeprefix("/report")])
    if not report.isspace():
        await bot.send_message(admin, report)
        await message.reply("Баг-репорт успешно отправлен. Разработчик ознакомится с информацией.")
    else:
        await message.reply("Мне нечего передать разработчику.")

@dp.message_handler(commands=["wiki_get"])
async def wiki_get(message):
    if message.text[10] == "(" and message.text[-1] == ")":
        request = message.text[12:-2:1]
        await message.reply(get_wiki_note(request=request))
    else:
        await message.reply("Ваша команда имеет неверное форматирования. Для просмотра синтаксиса команд /help_demy")

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
    #member = str(message.text).removeprefix('/ban')
    admin_rights = await message.chat.get_member(message.from_user.id)
    dump = json.dumps(dict(admin_rights))

    if '"can_restrict_members": true' in dump and message.reply_to_message:
        try:
            await bot.kick_chat_member(chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id)  #
            await bot.send_message(message.chat.id,
                                   f"Пользователь {message.reply_to_message.from_user.mention} забанен")
        except:
            await message.reply(f"Я не могу забанить {message.reply_to_message.from_user.mention}")
    else:
        await bot.send_message(message.chat.id, "У вас недостаточно прав, чтобы забанить пользователя")


@dp.message_handler(commands=["unban"], is_chat_admin=True)
async def unban(message):
    admin_rights = await message.chat.get_member(message.from_user.id)
    dump = json.dumps(dict(admin_rights))
    if '"can_restrict_members": true' in dump and message.reply_to_message:
        try:
            await message.bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            await bot.send_message(message.chat.id, "Пользователь разбанен")
        except:
            await bot.send_message(message.chat.id, "Что-то пошло не так, разбаньте пользователя вручную")
    else:
        await bot.send_message(message.chat.id, "У вас недостаточно прав")


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

                case "video":
                    await switch_types(message=message,
                                       phrase=msg,
                                       file_id=message.reply_to_message.video.file_id,
                                       type="video")
                case "voice":
                    await switch_types(message=message,
                                       phrase=msg,
                                       file_id=message.reply_to_message.voice.file_id,
                                       type="animation")

                case "animation":  # 15_728_640
                    await switch_types(message=message,
                                       phrase=msg,
                                       file_id=message.reply_to_message.animation.file_id,
                                       type="animation")

                case "photo":
                    await switch_types(
                                       message=message,
                                       phrase=msg,
                                       file_id=message.reply_to_message.photo[-1].file_id,
                                       type="photo")
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
            phrase=msg)
        await message.reply(rem_bind)
    else:
        await message.reply('Ваша команда имеет неверный вид.\n'
                            'Unbind должен иметь следующий вид: /unbind ("ваша фраза")\n'
                            'т.е. аргументы для команды передаются в скобках и ковычках, с отступом в один пробел от самоый команды.')


@dp.message_handler(content_types=['text'])
async def filter_messages(message: types.Message):
    bind = await get_binds(chat_id=int(message.chat.id))
    for elem in bind:
        if elem[1].lower() in message.text.lower():
            match elem[0]:

                case "text":
                    await message.reply(str(elem[2]))

                case "voice":
                    await message.reply_voice(voice=str(elem[2]))

                case "video":
                    await message.reply_video(video=str(elem[2]))

                case "animation":
                    await message.reply_animation(animation=str(elem[2]))

                case "photo":
                    await message.reply_photo(photo=str(elem[2]))
                case "sticker":
                    await message.reply_sticker(str(elem[2]))

                case _:
                    await bot.send_message(message.chat.id, "Хотел я отрпавить бинд, но что-то пошло не так...")


if __name__ == '__main__':
    executor.start_polling(dp)

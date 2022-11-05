from dataset import API_TOKEN, developer, database
import logging
import json
from pathlib import Path
import os
import subprocess
import emoji
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ContentType, Message, File
from db_ops import *


from support_methods import *


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['help_demy', "help"])
async def send_welcome(message: types.Message):
    await message.reply("Привет, я админ-бот Дементий от @Harfile\n"
                        "вот мой функционал на данный момент:\n"
                        '/bind ваша фраза - можно добавить бинд, который будет срабатывать на определенное слово '
                        'или фразу. Чтобы воспользоваться функцией, нужно после команды, отступив пробел, написать'
                        ' фразу-триггер. \nТриггер можно снять командой /unbind, команда имеет '
                        'аналогичный с /bind синтаксис.\n' 
                        'Сейчас доступны следующие типы триггеров: текст, видео, голосовые сообщения, видео, фото, gif,'
                        'стикеры и видеозаписи ("кружки").\n'
                        '/unbind_all - удаляет все бинды в чате, ЭТО ДЕЙСТВИЕ НЕЛЬЗЯ ОТМЕНИТЬ!'
                        ' (доступно только для админов)\n'
                        '/view_all_binds - показывает все бинды в вашем чате\n'
                        '/echo - отправитель сообщения закукарекает.\n'
                        '/dice - бросает кость, через пробел можно указать число бросков, но не более 10.\n'
                        '/wiki_get название статьи - команда возвращает статью на Википедии. Если существуют '
                        'только похожие статьи, возвращает их название. Если ничего из, то ошибку\n'
                        '/ban и /unban - в ответ на сообщение банит пользователя\n'
                        '/mobilize - мобилизует пользователя\n'
                        '/report - отправить репорт разработчику, будь то жалоба или предложение. после слова /report '
                        'оставьте текст\n'
                        'Бот работает некорректно?\n'
                        '-Бот должен являться администратором\n'
                        '-Бовым участникам чата должны быть видны ве сообщения\n'
                        '-Бот должен иметь право писать сообщения в чате.\n'
                        'Если все эти меры предприняты, но Бот по-прежнему работает некорректно, '
                        'то составьте баг-репорт, в котором опишите вашу проблему и то, как вы пытались ее решить.')


@dp.message_handler(commands=['echo'])
async def echo(message):
    if message.reply_to_message:
        msg = str(message.reply_to_message.text)
        await message.reply(f"Петух по имени {message.reply_to_message.from_user.mention} кукарекнул: {msg}")

@dp.message_handler(commands=["dev_note"])
async def get_db(message):
    if message.from_user.id == developer:
        note = str(message.text).removeprefix("/dev_note ")
        ids = get_ids()
        for i in ids:
            await bot.send_message(i, f"#Дневник_разработки\n#dev_blog\n{note}")
    else:
        message.reply_to_message("У вас нет доступа к этой функции")

@dp.message_handler(commands=["demotivator"])
async def demotivator(message):
    path = f"templates/demotivators/{message.reply_to_message.photo[-1].file_id}"
    await message.reply_to_message.photo[-1].download(path+".jpg")
    text = message.text.removeprefix("/demotivator ")
    await make_demotivator(path+".jpg", text)
    await message.reply_photo(open(path+".jpg", "rb"))
    os.remove(path+".jpg")


@dp.message_handler(commands=["mobilize"])
async def mobilize(message):
    if message.reply_to_message:
        with open("templates/mobilize.jpg", 'rb') as pht:
            await message.reply_to_message.reply_photo(pht)
    else:
        pass

@dp.message_handler(commands=["report"])
async def send_report(message):
    report = "\n".join([message.from_user.mention, str(message.text).removeprefix("/report")])
    if not report.isspace():
        await bot.send_message(developer, report)
        await message.reply("Баг-репорт успешно отправлен. Разработчик ознакомится с информацией.")
    else:
        await message.reply("Мне нечего передать разработчику.")


@dp.message_handler(commands=["wiki_get"])
async def wiki_get(message):
    try:
        request = message.text.removeprefix("/wiki_get ")
        await message.reply(get_wiki_note(request=request))

    except Exception as e:
        await message.reply(f"Что-то пошло не так! Вот текст ошибки:\n {e} \n Отправьте ее разработчику с помощью команды /report")


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
    add_chat_id(message.chat.id)
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
    msg = (message.text.removeprefix("/bind ")).lower()
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
                await switch_types(
                    message=message,
                    phrase=msg,
                    file_id=message.reply_to_message.sticker.file_id,
                    type="sticker"
                )

            case "video_note":
                await switch_types(
                                   message=message,
                                   phrase=msg,
                                   file_id=message.reply_to_message.video_note.file_id,
                                   type="video_note")

            case _:
                await message.reply("Биндов такого типа пока не завезли)")


    else:
        await message.reply("Что биндить-то?")


@dp.message_handler(commands=["unbind"])
async def remove_bind(message):
    try:
        msg = (message.text.removeprefix("/unbind ")).lower()
    except Exception as e:
        await message.reply(f"Что-то пошло не так, возмжно, неверное форматирование. Вот текст ошибки {e}")
        pass
    if not msg.isspace():
        rem_bind = remove_binds(
        message.chat.id,
        msg)
        await message.reply(rem_bind)
    else:
        await message.reply('Ваша команда имеет неверный вид.')


@dp.message_handler(commands=["unbind_all"], is_chat_admin=True)
async def remove_all_binds(message):
    rem_bind = remove_binds(
        chat_id=message.chat.id)
    await message.reply(rem_bind)


@dp.message_handler(commands=["view_all_binds"])
async def view_all_binds(message):
    binds = await get_binds(chat_id=message.chat.id)
    phrases = [i[1] for i in binds]
    if phrases != []:
        str_phrases = "\n".join(set(sorted(phrases)))
        await message.reply(str_phrases)
    else:
        await message.reply("В вашем чате нет биндов")


@dp.message_handler(content_types=['text'])
async def filter_messages(message: types.Message):
    bind = await get_binds(chat_id=message.chat.id)
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

                case "video_note":
                    await  message.reply_video_note(str(elem[2]))

                case _:
                    await bot.send_message(message.chat.id, "Хотел я отрпавить бинд, но что-то пошло не так...")


if __name__ == '__main__':
    executor.start_polling(dp)


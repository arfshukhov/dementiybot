from peewee import *

import os

db = SqliteDatabase('binds.db')


class Binds(Model):
    chat_id = IntegerField(null=False)
    type = CharField(null=False)
    phrase = TextField(null=False)
    answer = TextField(null=False)

    class Meta:
        database = db

with db:
    db.create_tables([Binds])


def add_new_bind(chat_id, type, phrase, answer):
    try:
        bind = Binds(chat_id=int(chat_id), type=str(type), phrase=str(phrase), answer=str(answer)).save()
        return "Бинд успешно добавлен!"
    except:
        return "Что-то пошло не так. Попробуйте заново или оставьте баг-репорт"


async def get_binds(chat_id):
    answers = []
    for binds in Binds.select().where(Binds.chat_id == chat_id):
        print(binds)
        answers.append([binds.type, binds.phrase, binds.answer])
        print(answers)
    return answers


def remove_binds(id, phras):
    try:
        binds = []
        for bind in Binds.select().where(Binds.phrase == phras, Binds.chat_id == id):
            binds.append([bind.type, bind.answer])
            print(binds)
        for bind_ in binds:
            path = os.getcwd()
            match bind_[0]:
                case "text":
                    rem_binds = Binds.delete().where(Binds.chat_id == id, Binds.phrase == phras).execute()
                case "voice":
                    path += r"\\audio\\"+bind_[1]
                    os.remove(path)
                    rem_binds = Binds.delete().where(Binds.chat_id == id, Binds.phrase == phras).execute()
                case "video":
                    path += r"\\video\\"+bind_[1]
                    os.remove(path)
                    rem_binds = Binds.delete().where(Binds.chat_id == id, Binds.phrase == phras).execute()
                case "animation":
                    path += r"\\animation\\" + bind_[1]
                    os.remove(path)
                    rem_binds = Binds.delete().where(Binds.chat_id == id, Binds.phrase == phras).execute()
                case "photo":
                    path += r"\\photo\\"
                    os.remove(path)
                    rem_binds = Binds.delete().where(Binds.chat_id == id, Binds.phrase == phras).execute()
                case "sticker":
                    rem_binds = Binds.delete().where(Binds.chat_id == id, Binds.phrase == phras).execute()
                case _:
                    pass

            return "Бинд успешно удален"
    except:

        return "Что-то пошло не так.\nПопробуйте снова или отправьте баг-репорт"

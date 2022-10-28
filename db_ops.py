from peewee import *
from dataset import *
import os

db = PostgresqlDatabase(database=database, host=host, user=user, port=5432, password=password)


class Binds(Model):
    chat_id = TextField(null=False)
    type = TextField(null=False)
    phrase = TextField(null=False)
    answer = TextField(null=False)

    class Meta:
        database = db
        db_table = "Binds"

db.connect()
db.create_tables([Binds])


def add_new_bind(chat_id, type, phrase, answer):
    #try:
    bind = Binds(chat_id=str(chat_id), type=str(type), phrase=str(phrase), answer=str(answer)).save()
    return "Бинд успешно добавлен!"
    #except:
    #    return "Что-то пошло не так. Попробуйте заново или оставьте баг-репорт"


async def get_binds(chat_id):
    answers = []
    for binds in Binds.select().where(Binds.chat_id == int(chat_id)):
        answers.append([binds.type, binds.phrase, binds.answer])
    return answers


def remove_binds(chat_id, phrase):
    try:
        id = int(chat_id)
        binds = []
        for bind in Binds.select().where(Binds.phrase == phrase, Binds.chat_id == id):
            binds.append([bind.type, bind.answer])
        for bind_ in binds:
            path = os.getcwd()
            match bind_[0]:
                case "text":
                    rem_binds = Binds.delete().where(Binds.chat_id == id, Binds.phrase == phrase).execute()
                case "voice":
                    rem_binds = Binds.delete().where(Binds.chat_id == id, Binds.phrase == phrase).execute()
                case "video":
                    rem_binds = Binds.delete().where(Binds.chat_id == id, Binds.phrase == phrase).execute()
                case "animation":
                    rem_binds = Binds.delete().where(Binds.chat_id == id, Binds.phrase == phrase).execute()
                case "photo":
                    rem_binds = Binds.delete().where(Binds.chat_id == id, Binds.phrase == phrase).execute()
                case "sticker":
                    rem_binds = Binds.delete().where(Binds.chat_id == id, Binds.phrase == phrase).execute()
                case _:
                    pass

            return "Бинд успешно удален"
    except:

        return "Что-то пошло не так.\nПопробуйте снова или отправьте баг-репорт"

from peewee import *

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


def remove_binds(chat_id, phrase):
    try:
        rem_binds = Binds.delete().where(Binds.chat_id == chat_id, Binds.phrase == phrase)
        return "Бинд успешно удален"
    except:
        return "Что-то пошло не так. Попробуйте снова или отправьте баг-репорт"

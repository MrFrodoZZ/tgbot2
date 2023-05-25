from telebot import TeleBot
from xml.dom import minidom
from requests import get
import sqlite3

bot = TeleBot(token="6173750891:AAHh6JY7OWCKZWoOhsR6Xtod0RqDCLkqqVA")


def create_session(comm=False):
    db = sqlite3.connect('db.db')
    if not comm:
        sql = db.cursor()
        return sql
    else:
        db.commit()


def answers_pool(tag):
    with open('ans/' + tag + '.txt', encoding='utf-8') as answer:
        return ''.join(s for s in answer.readlines())


def read_xml():
    resp = get('https://yakit.ru/rasp/rasp.xml')
    print(resp.text.encode('iso-5589-1').decode('utf-8'))


def parse(msg):
    return msg.from_user.id, msg.text


@bot.message_handler(commands=['start', 'help'])
def start_message(msg):
    user, text = parse(msg)
    sql = create_session()
    val = sql.execute(f'SELECT * FROM users WHERE teleid = {user}').fetchone()
    val1 = sql.execute(f'SELECT * FROM teachers WHERE teleid = {user}').fetchone()
    if val:
        bot.send_message(user, answers_pool('start_old'))
    else:
        bot.send_message(user, answers_pool('start_new'))
        bot.register_next_step_handler(msg, register_user)
    if val1:
        bot.send_message(user, answers_pool('start_old_c'))


def register_user(msg):
    user, text = parse(msg)
    sql = create_session()
    vals = text.split()
    if len(vals) == 4:
        pend = sql.execute(f'SELECT id FROM courses WHERE name = {vals[-1]}').fetchone()
        vals.pop()
        vals.append(pend[0])
        sql.execute('INSERT INTO users VALUES (?, ?, ?)', vals)
        create_session(True)
        bot.send_message(user, answers_pool('registration_complete'))
    else:
        bot.send_message(user, answers_pool('wrong_register'))
        bot.register_next_step_handler(msg, register_user)


@bot.message_handler(commands=['schedule'])
def get_schedule(msg):
    user, text = parse(msg)
    read_xml()


@bot.message_handler(commands=['note'])
def create_note1(msg):
    user, text = parse(msg)
    bot.send_message(user, answers_pool('note_creating'))
    bot.register_next_step_handler(msg, create_note2)


def create_note2(msg):
    user, text = parse(msg)
    sql = create_session()
    pend = sql.execute(f'SELECT * FROM notes WHERE owner = {user}').fetchall()
    sql.execute('INSERT INTO notes VALUES (?, ?, ?)', (user, text, len(pend) + 1))
    bot.send_message(user, answers_pool('note_created'))


@bot.message_handler(commands=['shownote'])
def show_notes(msg):
    user, text = parse(msg)
    sql = create_session()
    pend = sql.execute(f'SELECT * FROM notes WHERE owner = {user}').fetchall()
    res = 'Ваши заметки:'
    for owner, text, order in pend:
        res += f'\n\n{order}. {text}'
    bot.send_message(user, res)


@bot.message_handler(commands=['direct'])
def send_direct(msg):
    user, text = parse(msg)
    bot.send_message(user, answers_pool('type_direct'))
    bot.register_next_step_handler(msg, send_direct_text)


def send_direct_text(msg):
    user, text = parse(msg)
    sql = create_session()
    to_user = sql.execute(f'SELECT teleid FROM teachers WHERE course = '
                          f'(SELECT id FROM courses WHERE id = '
                          f'(SELECT course FROM users WHERE id = {user}))').fetchone()
    bot.send_message(to_user, text)
    bot.send_message(user, answers_pool('direct_sent'))


@bot.message_handler(func=lambda x: True)
def others(msg):
    user, text = parse(msg)
    sql = create_session()
    teach = sql.execute(f"SELECT teleid FROM teachers WHERE teleid = {user}").fetchall()
    if user in teach:

        if text == ".help":
            bot.send_message(user, answers_pool('courator_help'))

        if text == ".sd" or text == ".showdirects":
            pend = sql.execute(f"SELECT text FROM directs WHERE toid = {user}").fetchall()
            froms = sql.execute(f'SELECT teleid, name FROM users WHERE teleid = '
                                f'(SELECT fromid FROM teachers WHERE toid = {user})').fetchall()
            res = 'Текущие неотвеченные сообщения:'
            for fromid, toid, text in pend:
                res += f'\n\n{text}'
            bot.send_message(user, res)

        if text == ".sa" or text == ".sendtoall":
            bot.send_message(user, answers_pool("send_to_all"))
            bot.register_next_step_handler(msg, send_to_all)


def send_to_all(msg):
    user, text = parse(msg)
    sql = create_session()
    pend = sql.execute(f'SELECT teleid FROM users WHERE course = '
                       f'(SELECT course FROM teachers WHERE teleid = {user})').fetchall()
    for pupil in pend:
        pendd = sql.execute(f'SELECT name FROM courses WHERE id = '
                            f'(SELECT course FROM teachers WHERE teleid = {user})').fetchone()
        bot.send_message(pupil, answers_pool('from_teacher') + pendd[0])
        bot.send_message(pupil, text)
    bot.send_message(user, answers_pool("sa_done"))


bot.infinity_polling()

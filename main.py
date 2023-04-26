from telebot import TeleBot
from xml.dom import minidom
from requests import get
import sqlite3

bot = TeleBot(token="6173750891:AAHh6JY7OWCKZWoOhsR6Xtod0RqDCLkqqVA")


def create_session():
    db = sqlite3.connect('db.db')
    sql = db.cursor()
    return sql


def answers_pool(tag):
    with open(tag + '.txt') as answer:
        return answer.read()


def read_xml():
    resp = get('https://yakit.ru/rasp/rasp.xml')
    print(resp.json())
    # mydoc = minidom.parse('')


def parse(msg):
    return msg.from_user.id, msg.text


@bot.message_handler(commands=['start', 'help'])
def start_message(msg):
    user, text = parse(msg)
    sql = create_session()
    val = sql.execute(f'SELECT * FROM users WHERE id = {user}').fetchone()
    if len(val):
        bot.send_message(user, answers_pool('start_old'))
    else:
        bot.send_message(user, answers_pool('start_new'))


@bot.message_handler(commands=['schedule'])
def get_schedule(msg):
    user, text = parse(msg)
    read_xml()


@bot.message_handler(commands=['note'])
def create_note(msg):
    user, text = parse(msg)


bot.infinity_polling()

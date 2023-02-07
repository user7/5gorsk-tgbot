import logging
import json
import re

from telegram import Update
from telegram import User
from telegram import ReplyKeyboardMarkup
from telegram import KeyboardButton
from telegram.ext import filters
from telegram.ext import MessageHandler
from telegram.ext import ApplicationBuilder
from telegram.ext import ContextTypes
from telegram.ext import CommandHandler

from smtplib import SMTP_SSL
from smtplib import SMTPException
from email.mime.text import MIMEText
from email import utils

logging.basicConfig(
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level = logging.INFO
)

config = None
with open('config.json', 'r', encoding = 'utf-8') as f:
    config = json.load(f)

class DocReply:
    def __init__(self, path):
        self.path = path
    def ext(self) -> str:
        return re.search('\.[^.]+$', self.path).group().lower()
    def is_photo(self) -> bool:
        return self.ext() in ['.jpg', '.jpeg', '.png', '.gif']

def docs(data):
    if isinstance(data, str):
        return DocReply(data)
    elif isinstance(data, list):
        return [docs(x) for x in data]
    else:
        raise RuntimeException(f'data must be a string or a list, got: {data}')

cmd_contacts = '✉️ Связаться с нами'
cmd_maint = '🏠Обслуживание дома'
cmd_edc = '☎️ ЕДЦ ЖКХ'
cmd_tariffs = '📃Тарифы'
cmd_domofon = '📲 Домофон'
cmd_water_zayava = '📄Заявления в бухгалтерию по воде'
cmd_water_meters = '💧Передать показания счетчиков воды'
cmd_cancel = 'Отмена'
cmd_yes = 'Да'
cmd_no = 'Нет'

msg_enter_apt = 'Номер квартиры:'
msg_enter_cold = 'Холодная вода:'
msg_enter_hot = 'Горячая вода:'
msg_welcome = 'Поздравляем, вы подписались на бот ЖСК Пятигорск!'
msg_need_number = 'Введите число!'
msg_accepted = 'Принято!'
msg_cancelled = 'Отменено!'

email = '3903782@mail.ru'

msg_contacts = f'''
☎Телефон правления +74953903782
⏰Приёмные часы: вторник, четверг с 18.00 до 20.00
📨E-mail: {email}
'''.strip()

msg_maint = f'''
🏠Обслуживающая компания ООО 'Доминвест': +74993756563 круглосуточно.
⚡️Электрик
🚰Сантехник
🗑Засор мусоропровода
🔨Плотник
🚨Аварийная служба
🧹Уборщик
❗️Работы на территории общедомового имущества проводятся БЕСПЛАТНО.
💰Личное имущество собственников обслуживается по утвержденному тарифу. Тарифы уточняйте по телефону!💸
'''.strip()

msg_edc = [
    f'''
💻Единый диспетчерский центр (ЕДЦ) ЖКХ: +74955395353, аналог портала Наш город
❗️Заявки по любым вопросам, связанным с обслуживанием дома, если это не в компетенции Доминвест +74993756563❗️
🗑Забиты мусорки у дома
☃️Сугробы на стоянке
🌱Обрезка кустов, сухостой, падающие деревья
🌞Нет освещения у дома
'''.strip(),

    'https://gorod.mos.ru/'
]

msg_tariffs = [
    docs(config['tariffs']),
    '👩🏼‍🌾ГКУ ГЦЖС - http://www.subsident.ru/ Вся информация о субсидиях и льготах в сфере ЖКХ на территории Москвы.'
]

msg_domofon = f'''
📲Заказ ключей и ремонт домофона +74953957709
'''.strip()

msg_water_zayava = [
    docs(config['zayavas']),
    f'''
❗️Если в квартире никто не проживает, подайте заявление на расчёт воды исходя из нулевых показаний (бланк 1).
❗️Если не хотите снимать показания ежемесячно, подайте заявление на расчёт по среднесезонным показаниям (бланк 2).
📝Заявление можно передать через консьержа или прислать фотографию на почту {email}.
'''.strip()
]

keyboard_main = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(cmd_contacts)],
        [KeyboardButton(cmd_maint), KeyboardButton(cmd_edc)],
        [KeyboardButton(cmd_tariffs), KeyboardButton(cmd_domofon)],
        [KeyboardButton(cmd_water_zayava), KeyboardButton(cmd_water_meters)],
    ],
    resize_keyboard = True)

keyboard_cancel = ReplyKeyboardMarkup(
    keyboard = [[KeyboardButton(cmd_cancel)]],
    resize_keyboard = True)

keyboard_confirm = ReplyKeyboardMarkup(
    keyboard = [[KeyboardButton(cmd_yes), KeyboardButton(cmd_no)]],
    resize_keyboard = True)

# chat_id -> state
chat_state = {}

state_main = 1

class StateWater:
    def __init__(self):
        self.apt = None
        self.cold = None
        self.hot = None

    def __str__(self):
        return f'StateWater({self.apt}, {self.cold}, {self.hot})'

    def is_last_step(self):
        return None not in (self.apt, self.cold, self.hot)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = msg_welcome,
            reply_markup = keyboard_main)

def make_full_name(user):
    good_names = [w for w in [user.first_name, user.last_name, f'(id {user.id})'] if w is not None]
    return ' '.join(good_names)

def record_water(user, state):
    full_name = make_full_name(user)
    try:
        email = config['email']
        host = email['host']
        port = email['port']
        login = email['login']
        pass_ = email['pass']
        recepient = email['recepient']
        sender = utils.formataddr(('Бот Пятигорск', login), charset='utf-8')
        with SMTP_SSL(host = host, port = port) as smtp:
            smtp.login(login, pass_)
            msg = MIMEText(f'Это сообшение от телеграм бота. Пользователь {full_name} передал показания воды для квартиры {state.apt}. Холодная вода {state.cold}, горячая вода {state.hot}.')
            msg['Subject'] = f'вода кв {state.apt}, хол {state.cold}, гор {state.hot}'
            msg['From'] = sender
            msg['To'] = recepient
            smtp.sendmail(sender, recepient, msg.as_string())
            logging.info(f'water record sent {full_name} {state}')
            smtp.quit()
    except SMTPException as e:
        logging.info(f'error sending water record {full_name} {state}: {e}')

def check_input_int(input_, reply_cur, reply_next):
    try:
        i = int(input_)
        return (i, reply_next)
    except:
        return (None, [msg_need_number, reply_cur])

async def respond(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmd = update.message.text
    chat_id = update.effective_chat.id
    if chat_id not in chat_state:
        chat_state[chat_id] = state_main
    state = chat_state[chat_id]
    reply = None
    newstate = state_main

    logging.info('user={} command={}'.format(\
            make_full_name(update.message.from_user),\
            cmd if len(cmd) < 30 else cmd[0:30] + '...'))
    if cmd == cmd_contacts:
        reply = msg_contacts
    elif cmd == cmd_maint:
        reply = msg_maint
    elif cmd == cmd_edc:
        reply = msg_edc
    elif cmd == cmd_tariffs:
        reply = msg_tariffs
    elif cmd == cmd_domofon:
        reply = msg_domofon
    elif cmd == cmd_water_zayava:
        reply = msg_water_zayava
    elif cmd == cmd_cancel:
        reply = msg_cancelled
        newstate = state_main
    elif cmd == cmd_water_meters:
        reply = msg_enter_apt
        newstate = StateWater()
    elif isinstance(state, StateWater):
        newstate = state
        if state.apt is None:
            (state.apt, reply) = check_input_int(cmd, msg_enter_apt, msg_enter_cold)
        elif state.cold is None:
            (state.cold, reply) = check_input_int(cmd, msg_enter_cold, msg_enter_hot)
        elif state.hot is None:
            (state.hot, reply) = check_input_int(
                    cmd, msg_enter_hot,
                    f'Квартира {state.apt}, холодная вода {state.cold}, горячая вода {cmd.strip()}, всё верно?')
        else:
            newstate = state_main
            if cmd == cmd_yes:
                record_water(update.message.from_user, state)
                reply = msg_accepted
            else:
                reply = msg_cancelled
    else:
        newstate = state_main
        reply = 'Неизвестная команда'

    keyboard = None
    if newstate == state_main:
        keyboard = keyboard_main
    elif isinstance(newstate, StateWater):
        if newstate.is_last_step():
            keyboard = keyboard_confirm
        else:
            keyboard = keyboard_cancel
    chat_state[chat_id] = newstate

    await send_recursive(context, chat_id, keyboard, reply)

async def send_recursive(context: ContextTypes.DEFAULT_TYPE, chat_id, markup, reply):
    if reply is None:
        return
    elif isinstance(reply, str):
        await context.bot.send_message(chat_id = chat_id, text = reply, reply_markup = markup)
    elif isinstance(reply, list):
        for ir, r in enumerate(reply):
            m = markup if ir + 1 == len(reply) else None # attach markup only to the last message
            await send_recursive(context, chat_id, m, r)
    elif isinstance(reply, DocReply):
        doc = open(reply.path, 'rb')
        if reply.is_photo():
            await context.bot.send_photo(chat_id, doc, reply_markup = markup)
        else:
            await context.bot.send_document(chat_id, doc, reply_markup = markup)
    else:
        logging.info(f'unable to send an object of unsupported type: {reply}')

if __name__ == '__main__':
    application = ApplicationBuilder().token(config['token']).build()
    start_handler = CommandHandler('start', start)
    common_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), respond)
    application.add_handler(start_handler)
    application.add_handler(common_handler)
    application.run_polling()


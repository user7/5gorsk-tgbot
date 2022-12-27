import logging
import json

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

cmd_contacts = "✉️ Связаться с нами"
cmd_maint = "🏠Обслуживание дома"
cmd_edc = "☎️ ЕДЦ ЖКХ"
cmd_tariffs = "📃Тарифы 2022"
cmd_domofon = "📲 Домофон"
cmd_water_zayava = "📄Заявления в бухгалтерию по воде"
cmd_water_meters = "💧Передать показания счетчиков воды"
cmd_cancel = "Отмена"
cmd_yes = "Да"
cmd_no = "Нет"

msg_enter_apt = "Номер квартиры:"
msg_enter_cold = "Холодная вода:"
msg_enter_hot = "Горячая вода:"
msg_welcome = "Поздравляем! Вы подписались на бот ЖСК Пятигорск."

email = "3909322@mail.ru"

msg_contacts = f"""
☎Телефон +74953909322
⏰Часы работы Правления: каждый четверг с 18.00 до 20.00
📨E-mail: {email}
""".strip()

msg_maint = f"""
🏠Обслуживающая компания ООО "Доминвест": +74993756563 круглосуточно.
⚡️Электрик
🚰Сантехник
🗑Засор мусоропровода
🧹Уборщик
❗️Работы на территории общедомового имущества проводятся БЕСПЛАТНО.
💰Личное имущество собственников обслуживается по утвержденному тарифу. Тарифы уточняйте по телефону!💸
""".strip()

# TODO second message must be https://gorod.mos.ru/
msg_edc = f"""
💻Единый диспетчерский центр (ЕДЦ) ЖКХ: +74955395353, аналог портала Наш город
❗️Заявки по любым вопросам, связанным с обслуживанием дома, если это не в компетенции Доминвест +74993756563❗️
🗑Забиты мусорки у дома
☃️Сугробы на стоянке
🌱Обрезка кустов, сухостой, падающие деревья
🌞Нет освещения у дома
""".strip()

msg_tariffs = "jpeg" # TODO

msg_domofon = f"""
📲Обслуживание домофона +74950880888
🛠Заказ/ремонт ключей домофона +7495631193
""".strip()

# TODO pdf, pdf
msg_water_zayava = f"""
❗️Для тех, кто не проживает, или забывает подать показания, выше два бланка, которые необходимо предоставить в бухгалтерию.
📥По почте {email} или в ящики Правления на 1-х этажах.📪
📝Заявление можно написать в произвольной форме от руки и прислать фотографию.
""".strip()

keyboard_main = ReplyKeyboardMarkup(keyboard = [
    [KeyboardButton(cmd_contacts)],
    [KeyboardButton(cmd_maint), KeyboardButton(cmd_edc)],
    [KeyboardButton(cmd_tariffs), KeyboardButton(cmd_domofon)],
    [KeyboardButton(cmd_water_zayava), KeyboardButton(cmd_water_meters)],
])

keyboard_cancel = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(cmd_cancel)]])
keyboard_confirm = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(cmd_yes), KeyboardButton(cmd_no)]])

# chat_id -> state
chat_state = {}

state_main = 1

class StateWater:
    def __init__(self):
        self.apt = None
        self.cold = None
        self.hot = None

    def __str__(self):
        return f"StateWater({self.apt}, {self.cold}, {self.hot})"

    def is_last_step(self):
        return None not in (self.apt, self.cold, self.hot)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = msg_welcome,
            reply_markup = keyboard_main)

def record_water(user, state):
    email = config['email']
    login = email['login']
    with SMTP_SSL(host = email['host'], port = int(email['port'])) as smtp:
        smtp.login(login, email['pass'])
        msg = MIMEText('Это сообшение от телеграм бота. Пользователь {user} передал показания воды.')
        msg['Subject'] = f"вода {state.apt}: хол {state.cold}, гор {state.hot}"
        sender = utils.formataddr(('Бот Пятигорск', login), charset='utf-8')
        recepient = email['recepient']
        msg['From'] = sender
        msg['To'] = recepient
        print(smtp.sendmail(sender, recepient, msg.as_string()))
        smtp.quit()
    # TODO store in sqlite, ensure email has been sent

async def respond(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmd = update.message.text
    chat_id = update.effective_chat.id
    if chat_id not in chat_state:
        chat_state[chat_id] = state_main
    state = chat_state[chat_id]
    reply = None
    newstate = state_main
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
    elif cmd == cmd_water_meters:
        reply = msg_enter_apt
        newstate = StateWater()
    elif isinstance(state, StateWater):
        newstate = state
        if state.apt is None:
            state.apt = cmd
            reply = msg_enter_cold
        elif state.cold is None:
            state.cold = cmd
            reply = msg_enter_hot
        elif state.hot is None:
            state.hot = cmd
            reply = f"Квартира {state.apt}, холодная вода {state.cold}, горячая вода {state.hot}, всё верно?"
        elif cmd == cmd_yes:
            record_water(update.user, state)
            newstate = state_main
            reply = "Принято!"
        else:
            newstate = StateWater()
    else:
        reply = "Неизвестная команда"
        newstate = state_main

    keyboard = None
    if newstate == state_main:
        keyboard = keyboard_main
    elif isinstance(newstate, StateWater):
        if newstate.is_last_step():
            keyboard = keyboard_confirm
        else:
            keyboard = keyboard_cancel
    chat_state[chat_id] = newstate

    await context.bot.send_message(chat_id = chat_id, text = reply, reply_markup = keyboard)

if __name__ == '__main__':
    application = ApplicationBuilder().token(config["token"]).build()
    start_handler = CommandHandler('start', start)
    common_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), respond)
    application.add_handler(start_handler)
    application.add_handler(common_handler)
    application.run_polling()


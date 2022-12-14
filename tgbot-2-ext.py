import logging
from telegram import Update
from telegram import User
from telegram.ext import filters
from telegram.ext import MessageHandler
from telegram.ext import ApplicationBuilder
from telegram.ext import ContextTypes
from telegram.ext import CommandHandler

logging.basicConfig(
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level = logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id = update.effective_chat.id, text = "I'm a bot, talk!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Message from: " + str(update.message.from_user))
    print("Effective chat: " + str(update.effective_chat))
    chat_id1 = update.effective_chat.id
    chat_id2 = 964632818
    await context.bot.send_message(chat_id = chat_id1, text = update.message.text)
    if chat_id1 != chat_id2:
        await context.bot.send_message(
                chat_id = chat_id2,
                text = "message to {}: {}".format(chat_id1, update.message.text))

if __name__ == '__main__':
    with open('token.txt') as f:
        token = f.readline().rstrip()
    application = ApplicationBuilder().token(token).build()
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.run_polling()


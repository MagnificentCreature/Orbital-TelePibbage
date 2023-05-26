from Controller import conf
from Controller import BotCommands
import logging
from telegram.ext import ApplicationBuilder, CommandHandler

BOT_TOKEN = conf.BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    start_handler = CommandHandler('start', BotCommands.start)
    create_room_handler = CommandHandler('create_room', BotCommands.create_room)
    join_room_handler = CommandHandler('join_room', BotCommands.join_room)
    generate_handler = CommandHandler('generate', BotCommands.generate)
    application.add_handler(start_handler)
    application.add_handler(create_room_handler)
    application.add_handler(join_room_handler)
    application.add_handler(generate_handler)
    application.run_polling()
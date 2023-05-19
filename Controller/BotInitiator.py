import conf
import BotCommands
import logging
from telegram.ext import ApplicationBuilder, CommandHandler

BOT_TOKEN = conf.BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    start_handler = CommandHandler('start', BotCommands.start)
    application.add_handler(start_handler)
    
    application.run_polling()
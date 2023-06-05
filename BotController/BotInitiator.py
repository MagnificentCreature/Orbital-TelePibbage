import conf
from BotController import BotCommands
import logging
from telegram.ext import (
    ApplicationBuilder,
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

BOT_TOKEN = conf.TELE_BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

FRESH, INROOM, INGAME, PROMPTING_PHASE, LYING_PHASE, VOTING_PHASE = range(6)

def main() -> None:
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", BotCommands.start, block=False)],
        states={
            FRESH: [CommandHandler('create_room', BotCommands.create_room),
                    CommandHandler('join_room', BotCommands.join_room),
            ],
            INROOM: [
                CommandHandler('generate', BotCommands.generate)
            ],
        },
        fallbacks=[MessageHandler(filters.COMMAND, BotCommands.unknown)],
    )

    # start_handler = CommandHandler('start', BotCommands.start, block=False)
    # create_room_handler = CommandHandler('create_room', BotCommands.create_room)
    # join_room_handler = CommandHandler('join_room', BotCommands.join_room)
    # generate_handler = CommandHandler('generate', BotCommands.generate)
    # unknown_handler = MessageHandler(filters.COMMAND, BotCommands.unknown)

    # application.add_handler(start_handler)
    # application.add_handler(create_room_handler)
    # application.add_handler(join_room_handler)
    # application.add_handler(generate_handler)
    # application.add_handler(unknown_handler)

    application.add_handler(conv_handler)

    application.run_polling()
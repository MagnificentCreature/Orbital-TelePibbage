import conf
from BotController import BotCommands

import logging
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import (
    ApplicationBuilder,
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

BOT_TOKEN = conf.TELE_BOT_TOKEN

CREATE_ROOM, JOIN_ROOM, START_GAME = map(chr, range(3))

# State definitions for fresh level commands

# for FRESH
WelcomeKeyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text="Create Room", callback_data=str(CREATE_ROOM)),
        InlineKeyboardButton(text="Join Room", callback_data=str(JOIN_ROOM)),
    ],
])

# for INROOM
StartGameKeyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text="Start Game", callback_data=str(START_GAME)),
    ],
])

# for PROMPTING_PHASE
# StartGameKeyboard = InlineKeyboardMarkup([
#     [
#         InlineKeyboardButton(text="Enter Prompt", callback_data=str(ENTER_PROMPT)),
#     ],
# ])

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

FRESH, ENTERCODE, INROOM, INGAME, PROMPTING_PHASE, LYING_PHASE, VOTING_PHASE = range(7)

def main() -> None:
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", BotCommands.start, block=False)],
        states={
            FRESH: [CallbackQueryHandler(BotCommands.create_room, pattern="^" + str(CREATE_ROOM) + "$"),
                    CallbackQueryHandler(BotCommands.join_room_start, pattern="^" + str(JOIN_ROOM) + "$"),
            ],
            # [CallbackQueryHandler('create_room', BotCommands.create_room),
            #         CallbackQueryHandler('join_room', BotCommands.join_room),
            # ],
            ENTERCODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, BotCommands.join_room_code)],
            INROOM: [
                CallbackQueryHandler(BotCommands.start_game, pattern="^" + str(START_GAME) + "$"),
                CommandHandler('leave_room', BotCommands.leave_room),
            ],
            INGAME: [
                
                CommandHandler('generate', BotCommands.generate)
            ]
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
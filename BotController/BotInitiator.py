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

# State definitions for fresh level commands
CREATE_ROOM, JOIN_ROOM, START_GAME = map(chr, range(3))
# Entercode and In_room level commands
RETURN_TO_FRESH = map(chr, range(3,4))
#Shortcut for Conversation Handler END
END = ConversationHandler.END

# for FRESH
WelcomeKeyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text="Create Room", callback_data=str(CREATE_ROOM)),
        InlineKeyboardButton(text="Join Room", callback_data=str(JOIN_ROOM)),
    ],
])

# for Reentering Code
ReenterKeyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text="Back", callback_data=str(RETURN_TO_FRESH)),
    ],
])

# for Players in ENTER TEXT
StartGameKeyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text="Back", callback_data=str(RETURN_TO_FRESH)),
    ],
])

# for Hosts INROOM
StartGameKeyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text="Start Game", callback_data=str(START_GAME)),
    ],
    [
        InlineKeyboardButton(text="Back", callback_data=str(RETURN_TO_FRESH)),
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
                    CallbackQueryHandler(BotCommands.return_to_fresh, pattern="^" + str(RETURN_TO_FRESH) + "$")
            ],
            ENTERCODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, BotCommands.join_room_code),
                        CallbackQueryHandler(BotCommands.return_to_fresh, pattern="^" + str(RETURN_TO_FRESH) + "$")
            ],
            INROOM: [
                CallbackQueryHandler(BotCommands.start_game, pattern="^" + str(START_GAME) + "$"),
                CallbackQueryHandler(BotCommands.return_to_fresh, pattern="^" + str(RETURN_TO_FRESH) + "$"),
            ],
            INGAME: [
                
                CommandHandler('generate', BotCommands.generate)
            ]
        },
        fallbacks=[MessageHandler(filters.COMMAND, BotCommands.unknown)],
    )

    application.add_handler(conv_handler)

    application.run_polling()
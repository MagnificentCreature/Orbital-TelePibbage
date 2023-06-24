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
# In_game level commands
ENTER_PROMPT, ENTER_LIE, VOTE_LIE, VOTE_TRUTH = map(chr, range(4,8))
#Shortcut for Conversation Handler END
END = ConversationHandler.END
#VOTE REGEX
VOTE_REGEX = r"v:[^:]+:[^:]+"

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
WaitingKeyboard = InlineKeyboardMarkup([
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

FRESH, ENTERCODE, INROOM, WAITING_FOR_HOST, PROMPTING_PHASE, LYING_PHASE, VOTING_PHASE, REVEAL_PHASE = range(8)
#Shortcut for returning to FRESH
FRESH_CALLBACK = CallbackQueryHandler(BotCommands.return_to_fresh, pattern="^" + str(RETURN_TO_FRESH) + "$")

def main() -> None:
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # In game conversation handler
    game_conv_handler = ConversationHandler(
        entry_points=[
                CallbackQueryHandler(BotCommands.start_game, pattern="^" + str(START_GAME) + "$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, BotCommands.take_prompt),
            ],
        states={
            PROMPTING_PHASE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, BotCommands.take_prompt),
            ],
            LYING_PHASE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, BotCommands.take_lie),
            ],
            VOTING_PHASE: [
                CallbackQueryHandler(BotCommands.handle_vote_callback, pattern=VOTE_REGEX),
            ],
            REVEAL_PHASE: [
                # MessageHandler(filters.TEXT & ~filters.COMMAND, BotCommands.reveal_lies),
                MessageHandler(filters.COMMAND, BotCommands.unknown),
            ]
        },
        fallbacks=[MessageHandler(filters.COMMAND, BotCommands.unknown)],
        map_to_parent={
            WAITING_FOR_HOST: INROOM,
            INROOM: INROOM,
        }
    )

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    main_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", BotCommands.start)],
        states={
            FRESH: [CommandHandler("start", BotCommands.start),
                    CallbackQueryHandler(BotCommands.create_room, pattern="^" + str(CREATE_ROOM) + "$"),
                    CallbackQueryHandler(BotCommands.join_room_start, pattern="^" + str(JOIN_ROOM) + "$"),
            ],
            ENTERCODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, BotCommands.join_room_code),
                        FRESH_CALLBACK
            ],
            INROOM: [
                game_conv_handler,
                FRESH_CALLBACK,
            ],
        },
        fallbacks=[MessageHandler(filters.COMMAND, BotCommands.unknown)],
    )

    application.add_handler(main_conv_handler)

    application.run_polling()
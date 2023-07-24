import conf
from BotController import BotCommands
from BotController.BotInitiatorConstants import BotInitiatorConstants

import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

BOT_TOKEN = conf.TELE_BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

#Shortcut for returning to FRESH
FRESH_CALLBACK = CallbackQueryHandler(BotCommands.return_to_fresh, pattern="^" + str(BotInitiatorConstants.RETURN_TO_FRESH) + "$")

def main() -> None:
    application = ApplicationBuilder().token(BOT_TOKEN).read_timeout(30).write_timeout(30).build()
    
    # In game conversation handler
    game_conv_handler = ConversationHandler(
        entry_points=[
                CallbackQueryHandler(BotCommands.start_game, pattern="^" + str(BotInitiatorConstants.START_GAME) + "$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, BotCommands.take_prompt, block=False),
                CallbackQueryHandler(BotCommands.handle_arcade_gen, pattern=BotInitiatorConstants.SEND_ARCADE_WORD_REGEX),
            ],
        states={
            BotInitiatorConstants.PROMPTING_PHASE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, BotCommands.take_prompt, block=False),
            ],
            BotInitiatorConstants.LYING_PHASE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, BotCommands.take_lie),
            ],
            BotInitiatorConstants.VOTING_PHASE: [
                CallbackQueryHandler(BotCommands.handle_vote_callback, pattern=BotInitiatorConstants.VOTE_REGEX),
                CallbackQueryHandler(BotCommands.create_room, pattern="^" + str(BotInitiatorConstants.CREATE_ROOM) + "$"),
                CallbackQueryHandler(BotCommands.join_room_start, pattern="^" + str(BotInitiatorConstants.JOIN_ROOM) + "$"),
                CallbackQueryHandler(BotCommands.play_again, pattern=BotInitiatorConstants.PLAY_AGAIN_REGEX),
            ],
            BotInitiatorConstants.REVEAL_PHASE: [
                # MessageHandler(filters.TEXT & ~filters.COMMAND, BotCommands.reveal_lies),
                MessageHandler(filters.COMMAND, BotCommands.unknown),
            ], 
            BotInitiatorConstants.ARCADE_GEN_PHASE: [
                CallbackQueryHandler(BotCommands.handle_arcade_gen, pattern=BotInitiatorConstants.SEND_ARCADE_WORD_REGEX, block=False),
                CallbackQueryHandler(BotCommands.handle_arcade_prompt, pattern=BotInitiatorConstants.SEND_ARCADE_PROMPT_REGEX, block=False),
            ],
            BotInitiatorConstants.CAPTION_PHASE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, BotCommands.take_caption),
            ],
            BotInitiatorConstants.PICKING_PHASE: [
                CallbackQueryHandler(BotCommands.handle_pick, pattern=BotInitiatorConstants.CAPTION_REGEX),
            ],
            BotInitiatorConstants.BATTLE_PHASE: [
                CallbackQueryHandler(BotCommands.battle_vote_callback, pattern=BotInitiatorConstants.BATTLE_REGEX),
                CallbackQueryHandler(BotCommands.create_room, pattern="^" + str(BotInitiatorConstants.CREATE_ROOM) + "$"),
                CallbackQueryHandler(BotCommands.join_room_start, pattern="^" + str(BotInitiatorConstants.JOIN_ROOM) + "$"),
                CallbackQueryHandler(BotCommands.play_again, pattern=BotInitiatorConstants.PLAY_AGAIN_REGEX),
            ],
        },
        fallbacks=[MessageHandler(filters.COMMAND, BotCommands.unknown)],
        map_to_parent={
            BotInitiatorConstants.FRESH: BotInitiatorConstants.FRESH,
            BotInitiatorConstants.WAITING_FOR_HOST: BotInitiatorConstants.INROOM,
            BotInitiatorConstants.INROOM: BotInitiatorConstants.INROOM,
            BotInitiatorConstants.ENTERCODE: BotInitiatorConstants.ENTERCODE,
        })

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    main_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", BotCommands.start)],
        states={
            BotInitiatorConstants.FRESH: [CommandHandler("start", BotCommands.start),
                    CallbackQueryHandler(BotCommands.create_room, pattern="^" + str(BotInitiatorConstants.CREATE_ROOM) + "$"),
                    CallbackQueryHandler(BotCommands.join_room_start, pattern="^" + str(BotInitiatorConstants.JOIN_ROOM) + "$"),
                    CallbackQueryHandler(BotCommands.play_again, pattern=BotInitiatorConstants.PLAY_AGAIN_REGEX),
            ],
            BotInitiatorConstants.ENTERCODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, BotCommands.join_room_code),
                        FRESH_CALLBACK
            ],
            BotInitiatorConstants.INROOM: [
                game_conv_handler,
                CallbackQueryHandler(BotCommands.change_mode, pattern="^" + str(BotInitiatorConstants.CHANGE_MODE) + "$"),
                FRESH_CALLBACK,
            ],
        },
        fallbacks=[
                MessageHandler(filters.COMMAND, BotCommands.unknown),
            ],
    block=False)

    help_handler = CommandHandler("help", BotCommands.help)

    application.add_handler(main_conv_handler)
    application.add_handler(help_handler)
    
    application.run_polling()
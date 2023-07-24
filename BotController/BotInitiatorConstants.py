

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler


class BotInitiatorConstants():
    # State definitions for fresh level commands
    CREATE_ROOM, JOIN_ROOM, START_GAME = map(chr, range(3))
    # Entercode and In_room level commands
    RETURN_TO_FRESH, CHANGE_MODE = map(chr, range(3,5))
    # In_game level commands
    SEND_PROMPT, SEND_LIE, VOTE = map(chr, range(5,8))
    SEND_ARCADE_WORD, SEND_ARCADE_PROMPT, CAPTION, BATTLE_VOTE = map(chr, range(8,12))
    # End game restart commands
    PLAY_AGAIN = map(chr, range(12,13))
    #Shortcut for Conversation Handler END
    END = ConversationHandler.END
    #VOTE REGEX
    VOTE_REGEX = fr"{VOTE}:[^:]+"
    #regex for PLAY_AGAIN:Four uppercase letters
    PLAY_AGAIN_REGEX = f"{PLAY_AGAIN}" + ":[A-Z]{4}"
    SEND_ARCADE_WORD_REGEX = f"{SEND_ARCADE_WORD}:.*"
    SEND_ARCADE_PROMPT_REGEX = f"{SEND_ARCADE_PROMPT}:.*"
    CAPTION_REGEX = fr"{CAPTION}:[^:]+"
    BATTLE_REGEX = fr"{BATTLE_VOTE}:[^:]+"

    # for FRESH
    WelcomeKeyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="Create Room", callback_data=str(CREATE_ROOM)),
            InlineKeyboardButton(text="Join Room", callback_data=str(JOIN_ROOM)),
        ]
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
    StartGameButtons = [
        [
            InlineKeyboardButton(text="Start Game", callback_data=str(START_GAME)),
        ],
        [
            InlineKeyboardButton(text="Change to Arcade Game Mode", callback_data=str(CHANGE_MODE)),
        ],
        [
            InlineKeyboardButton(text="Back", callback_data=str(RETURN_TO_FRESH)),
        ],
    ]

    FRESH, ENTERCODE, INROOM, WAITING_FOR_HOST, PROMPTING_PHASE, LYING_PHASE, VOTING_PHASE, REVEAL_PHASE, ARCADE_GEN_PHASE, CAPTION_PHASE, PICKING_PHASE, BATTLE_PHASE = range(12)

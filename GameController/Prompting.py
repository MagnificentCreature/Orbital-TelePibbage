from telegram import InlineKeyboardMarkup, InlineKeyboardButton
prompt_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text="Enter Your Prompt!", callback_data="NOTHING"),
    ]
])

async def beginPhase1(bot, room):
    await sendPhase1Messages(bot, room)

async def sendPhase1Messages(bot, room):
    await room.broadcast(bot, "Phase1p1")
    await room.broadcast(bot, "Phase1p2", reply_markup=prompt_keyboard)

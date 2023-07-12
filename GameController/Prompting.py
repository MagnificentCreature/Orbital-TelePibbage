import asyncio
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from Chat.DialogueReader import DialogueReader

prompt_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text="Enter Your Prompt!", callback_data="NOTHING"),
    ]
])

async def beginPhase1(bot, room):
    await sendPhase1Messages(bot, room)

async def sendPhase1Messages(bot, room):
    await room.broadcast(bot, "Phase1p1")
    await asyncio.sleep(2)
    await room.broadcast(bot, "Phase1p2", reply_markup=prompt_keyboard, parse_mode=DialogueReader.MARKDOWN)

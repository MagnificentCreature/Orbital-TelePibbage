import asyncio
import random

from Player.PlayerConstants import PlayerConstants
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from Chat.DialogueReader import DialogueReader

lie_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text="Enter Your Lie!", callback_data="NOTHING"),
    ]
])

async def beginPhase2(bot, room):
    await sendPhase2Messages(bot, room)
    await room.broadCall(bot, sendNextImage)

async def sendPhase2Messages(bot, room):
    await room.broadcast(bot, "ArcadePhase2p1", parse_mode=DialogueReader.MARKDOWN)
    await asyncio.sleep(2)
    await room.broadcast(bot, "ArcadePhase2p2", parse_mode=DialogueReader.MARKDOWN)

async def sendNextImage(bot, room, player):
    imageList = await room.getRemainingImages(player)
    if len(imageList) <= 0:
        await player.deleteMessage("CaptionImage")
        player.deleteContext(PlayerConstants.NEXT_CAPTION.value)
        player.setItem(PlayerConstants.CAPTION, True)
        return False
    image = imageList.pop(random.randint(0, len(imageList) - 1))
    if image is None:
        print("NO IMAGE TO CAPTION")
    player.setItem(PlayerConstants.NEXT_CAPTION, image) # fill second param with image
    if not await player.queryMessagekey("CaptionImage"):
        await player.sendImageURL(bot, image.getImageURL(), messageKey="CaptionImage", caption="Phase2caption", **{"item": "caption"}) # , reply_markup=lie_keyboard
        return True
    await player.editImageURL("CaptionImage", image.getImageURL(), caption="Phase2caption", **{"item": "caption"}) # , reply_markup=lie_keyboard
    return True
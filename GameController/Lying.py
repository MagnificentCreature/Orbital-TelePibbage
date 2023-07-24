import asyncio
import random

from Player.Player import Player
from Player.PlayersManager import PlayersManager
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
    await room.broadcast(bot, "Phase2p1", parse_mode=DialogueReader.MARKDOWN)
    await asyncio.sleep(2)
    await room.broadcast(bot, "Phase2p2")

async def sendNextImage(bot, room, player):
    imageList = await room.getRemainingImages(player)
    if len(imageList) <= 0:
        await player.deleteMessage("LyingImage")
        player.deleteContext(Player.PlayerConstants.NEXT_LIE.value)
        player.setItem(Player.PlayerConstants.LIE, True)
        return False
    image = imageList.pop(random.randint(0, len(imageList) - 1))
    if image is None:
        print("NO IMAGE WTF LOL")
    player.setItem(Player.PlayerConstants.NEXT_LIE, image) # fill second param with image
    if not await player.queryMessagekey("LyingImage"):
        await player.sendImageURL(bot, image.getImageURL(), messageKey="LyingImage", caption="Phase2caption", **{"item": "lie"}) # , reply_markup=lie_keyboard
        return True
    await player.editImageURL("LyingImage", image.getImageURL(), caption="Phase2caption", **{"item": "lie"}) # , reply_markup=lie_keyboard
    return True
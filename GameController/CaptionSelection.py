import asyncio

from Player.Player import Player


async def beginPhase3(bot, room):
    await sendPhase3Messages(bot, room)
    await room.broadCall(bot, broadcast_image_captions)

async def sendPhase3Messages(bot, room):
    await room.broadcast(bot, "ArcadePhase3p1")
    
async def broadcast_image_captions(bot, room, player):
    image = player.queryItem(Player.PlayerConstants.ARCADE_IMAGE)
    await player.sendImageURL(bot, image.getImageURL(), reply_markup=image.getCaptionKeyboard())
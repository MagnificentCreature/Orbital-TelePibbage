import random

from Player.Player import Player
from Player.PlayersManager import PlayersManager

async def beginPhase2(bot, room):
    await sendPhase2Messages(bot, room)
    await room.broadCall(bot, sendNextImage)

async def sendPhase2Messages(bot, room):
    await room.broadcast(bot, "Phase2p1")
    await room.broadcast(bot, "Phase2p2")

async def sendNextImage(bot, room, player):
    # TODO: Send the player the next image he should come up with a lie for
    imageList = await room.getImageList(player)
    if len(imageList) <= 0:
        player.setItem(Player.PlayerConstants.NEXT_LIE, None)
        player.setItem(Player.PlayerConstants.LIE, True)
        player.deleteContext(Player.PlayerConstants.NEXT_LIE)
        return None
    image = imageList.pop(random.randint(0, len(imageList) - 1))
    player.setItem(Player.PlayerConstants.NEXT_LIE, image) # fill second param with image
    await player.sendImageURL(bot, image.getImageURL())


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
    imageList = await room.getRemainingImages(player)
    if len(imageList) <= 0:
        player.deleteContext(Player.PlayerConstants.NEXT_LIE.value)
        player.setItem(Player.PlayerConstants.LIE, True)
        return False
    image = imageList.pop(random.randint(0, len(imageList) - 1))
    player.setItem(Player.PlayerConstants.NEXT_LIE, image) # fill second param with image
    print("NEXT IMAGE: " + str(image.getImageURL()) + str(player.getUsername()) + str(Player.PlayerConstants.NEXT_LIE))
    await player.sendImageURL(bot, image.getImageURL())
    return True
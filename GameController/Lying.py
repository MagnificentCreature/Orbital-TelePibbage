from Player.Player import Player
from Player.PlayersManager import PlayersManager

async def beginPhase2(bot, room):
    await sendPhase2Messages(bot, room)

async def sendPhase2Messages(bot, room):
    await room.broadcast(bot, "Phase2p1")
    await room.broadcast(bot, "Phase2p2")

async def sendNextImage(bot, room, username):
    # TODO: Send the player the next image he should come up with a lie for
    player = PlayersManager.queryPlayer(username)
    room
    player.setItem(Player.PlayerConstants.NEXT_LIE) # fill second param with image
    return


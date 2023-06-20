async def beginPhase2(bot, room):
    await sendPhase2Messages(bot, room)

async def sendPhase2Messages(bot, room):
    await room.broadcast(bot, "Phase2p1")
    await room.broadcast(bot, "Phase2p2")

async def sendNextImage(bot, room, username):
    # TODO: Send the player the next image he should come up with a lie for
    return


async def beginPhase3(bot, room):
    await sendPhase3Messages(bot, room)

async def sendPhase3Messages(bot, room):
    await room.broadcast(bot, "Phase3p1")
    await room.broadcast(bot, "Phase3p2")
    await room.broadcast_voting_image(bot)
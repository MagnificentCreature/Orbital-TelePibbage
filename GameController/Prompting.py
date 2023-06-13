async def beginPhase1(bot, room):
    await sendPhase1Messages(bot, room)

async def sendPhase1Messages(bot, room):
    await room.broadcast(bot, "Phase1")

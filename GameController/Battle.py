from DialogueReader import DialogueReader


async def beginPhase4(bot, room):
    await sendPhase4Messages(bot, room)

async def sendPhase4Messages(bot, room):
    await room.broadcast(bot, "ArcadePhase4p1", parse_mode=DialogueReader.MARKDOWN)
    await room.broadcast(bot, "ArcadePhase4p2", parse_mode=DialogueReader.MARKDOWN)
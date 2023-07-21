import asyncio
from Chat.DialogueReader import DialogueReader

async def beginPhase3(bot, room):
    await sendPhase3Messages(bot, room)

async def sendPhase3Messages(bot, room):
    await room.broadcast(bot, "Phase3p1", parse_mode=DialogueReader.MARKDOWN)
    await asyncio.sleep(2)
    await room.broadcast(bot, "Phase3p2")
    await room.broadcast_voting_image(bot)
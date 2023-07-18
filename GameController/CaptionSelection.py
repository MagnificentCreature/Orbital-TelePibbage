import asyncio


async def beginPhase3(bot, room):
    await sendPhase3Messages(bot, room)
    await room.broadcast_image_captions

async def sendPhase3Messages(bot, room):
    await room.broadcast(bot, "Phase3p1")
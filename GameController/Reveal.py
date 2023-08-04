import asyncio

from Chat.DialogueReader import DialogueReader

async def beginPhase4(bot, room):
    await sendPhase4Messages(bot, room)
    await asyncio.sleep(3)
    await revealLeaderboard(bot, room)

async def sendPhase4Messages(bot, room):
    await room.broadcast(bot, "Phase4p1")
    await asyncio.sleep(2)
    await room.broadcast(bot, "Phase4p2")

# Method Unused
async def revealNextImage(bot, room, player):
    # TODO: Send the player the next image he should come up with a lie for
    imageList = await room.getImageListCopy() #This function should return a COPY of the image list
    
    for imageObj in imageList:

      player.sendImageURL(bot, imageObj.getImageURL())

      message = imageObj.showPlayersTricked()

      await player.send_message(bot, message, raw=True, parse_mode=DialogueReader.MARKDOWN) #unsafe method? , parse_mode=DialogueReader.MARKDOWN
    # message = await image.getMessage(PlayerConstants.NEXT_LIE)

async def revealLeaderboard(bot, room):
    leaderboardMsg = room.getLeaderboard()

    leaderboardMsg += '\n*Thanks for playing everyone\!*'

    await room.broadcast(bot, leaderboardMsg, raw=True, parse_mode=DialogueReader.MARKDOWN)
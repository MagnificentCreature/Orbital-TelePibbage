async def beginPhase4(bot, room):
    await sendPhase4Messages(bot, room)
    await room.broadCall(bot, revealNextImage)

async def sendPhase4Messages(bot, room):
    await room.broadcast(bot, "Phase4p1")
    await room.broadcast(bot, "Phase4p2")

async def revealNextImage(bot, room, player):
    # TODO: Send the player the next image he should come up with a lie for
    imageList = await room.getImageListCopy() #This function should return a COPY of the image list
    
    # Pop one form the image list and reveal it to the players
    imageObj = imageList.pop()

    player.sendImageURL(bot, imageObj.getImageURL())

    message = imageObj.showPlayersTricked()
    # player.sendMessage(bot, message)
    await bot.send_message(chat_id=player.getChatID(), text=message)
    # message = await image.getMessage(Player.PlayerConstants.NEXT_LIE)
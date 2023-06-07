def beginPhase1(bot, room):
    sendPhase1Messages(bot, room)

def sendPhase1Messages(bot, room):
    room.broadcast(bot, "Phase1")

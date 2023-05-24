"""
Class that holds data about rooms
"""

import asyncio
from Chat.DialogueReader import DialogueReader
from Player.PlayersManager import PlayersManager

class Room:
    code = ""
    host = ""
    players = [] #contains list of usernames
    MAX_PLAYERS = 8
    state = 0 # 0 = join state, 1 = game state

    def __init__(self, room, host):
        self.code = room
        self.host = host

    def getCode(self):
        return self.code
    
    # Dialogue messages to send when adding player
    async def sendRoomMessages(self, bot, username):
        await DialogueReader.sendMessage(bot, username, "RoomCode", **{'roomCode':self.getCode()})
        await DialogueReader.sendMessage(bot, username, "JoinRoom2", **{'playerCount':len(self.players), 'maxPlayerCount':str(self.MAX_PLAYERS)})
        await DialogueReader.sendMessage(bot, username, "Invite", **{'roomCode':self.getCode()})
        await DialogueReader.sendMessage(bot, username, "WaitingToStart")
        await asyncio.gather(
            *[DialogueReader.sendMessage(bot, player, "PlayerJoined", **{'player':username, 'playerCount':len(self.players), 'maxPlayerCount':str(self.MAX_PLAYERS)}) for player in self.players if player != username]
        )

    # Add player to room
    # Fails if is already in or if room is full
    async def addPlayer(self, username, action, bot):
        # do nothing if the player is already in the room
        if (username in self.players):
            await DialogueReader.sendMessage(bot, username, "AlreadyInRoom", **{'action':action})
            return False
        if len(self.players) == Room.MAX_PLAYERS:
            await DialogueReader.sendMessage(bot, username, "RoomFull", **{'action':action})
            return False
        if (PlayersManager.isPlayerFree(username)):
            await DialogueReader.sendMessage(bot, username, "InGame", **{'action':action})
            return False
        if (self.state == 1):
            await DialogueReader.sendMessage(bot, username, "GameInProgress")
            return False

        # What remains is when state is 0 and room has space to join
        await self.sendRoomMessages(bot, username)

        self.players.append(username)
        return True

    # Remove player from room
    # Fails if not in room 
    def removePlayer(self, player):
        if player not in self.players:
            return False
        if player == self.host:
            # if player is the host, delete the room
            del self #TODO: Make delete room code
            return True
        self.players.remove(player)
        return True

    def hasPlayer(self, username):
        return username in self.players
    
    def joinState(self):
        return self.state == 0
    
    # WIP this this will enable the features for audience to join
    def audienceState(self):
        return self.state == 1 
    
    def startGame(self):
        self.state = 1
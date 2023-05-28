"""
Class that holds data about rooms
"""

import asyncio
from Chat.DialogueReader import DialogueReader
from Player.PlayersManager import PlayersManager

class Room:
    code = ""
    host = None #player object
    players = [] #contains list of player objects
    MAX_PLAYERS = 8
    state = 0 # 0 = join state, 1 = game state

    def __init__(self, code, host):
        self.code = code
        self.host = host
        self.players = []
        self.state = 0

    def getCode(self):
        return self.code
    
    # Dialogue messages to send when adding player
    async def sendRoomMessages(self, bot, player):
        await player.sendMessage(bot, "RoomCode", **{'roomCode':self.getCode()})
        await player.sendMessage(bot, "JoinRoom2", **{'playerCount':len(self.players), 'maxPlayerCount':str(self.MAX_PLAYERS)})
        await player.sendMessage(bot, "Invite", **{'roomCode':self.getCode()})
        await player.sendMessage(bot, "WaitingToStart")
        await player.sendMessage(bot, "WaitingToStart2")
        await asyncio.gather(
            *[playerElem.sendMessage(bot, "PlayerJoined", **{'player':player.getUsername(), 'playerCount':len(self.players), 'maxPlayerCount':str(self.MAX_PLAYERS)}) for playerElem in self.players if playerElem != player]
        )

    # Add player to room
    # Fails if is already in or if room is full
    async def addPlayer(self, username, action, bot):
        player = PlayersManager.queryPlayer(username)
        # do nothing if the player is already in the room
        print(str(self.players) + self.code)
        if (player in self.players):
            await player.sendMessage(bot, "AlreadyInRoom", **{'action':action})
            return False
        if len(self.players) == Room.MAX_PLAYERS:
            await player.sendMessage(bot, "RoomFull", **{'action':action})
            return False
        if (not player.isFree()):
            await player.sendMessage(bot, "InGame", **{'action':action})
            return False
        if (self.state == 1):
            await player.sendMessage(bot, "GameInProgress")
            return False

        # What remains is when state is 0 and room has space to join
        self.players.append(player)
        await self.sendRoomMessages(bot, player)
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

    def hasPlayer(self, player):
        return player in self.players
    
    def joinState(self):
        return self.state == 0
    
    # WIP this this will enable the features for audience to join
    def acceptingAudience(self):
        return self.state == 1 
    
    def startGame(self):
        self.state = 1
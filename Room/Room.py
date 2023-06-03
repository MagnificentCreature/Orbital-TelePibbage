"""
Class that holds data about rooms
"""

import asyncio
from Player.PlayersManager import PlayersManager

class Room:
    _code = ""
    _host = None #player object
    _players = [] #contains list of player objects
    MAX_PLAYERS = 8
    _state = 0 # 0 = join state, 1 = game state

    def __init__(self, code, host):
        self._code = code
        self._host = host
        self._players = []
        self._state = 0

    def getCode(self):
        return self._code
    
    # Dialogue messages to send when adding player
    async def __sendRoomMessages(self, bot, player):
        await player.sendMessage(bot, "RoomCode", **{'roomCode':self.getCode()})
        await player.sendMessage(bot, "JoinRoom2", **{'playerCount':len(self._players), 'maxPlayerCount':str(self.MAX_PLAYERS)})
        await player.sendMessage(bot, "Invite", **{'roomCode':self.getCode()})
        await player.sendMessage(bot, "WaitingToStart")
        # await player.sendMessage(bot, "WaitingToStart2")
        await asyncio.gather(
            *[playerElem.sendMessage(bot, "PlayerJoined", **{'player':player.getUsername(), 'playerCount':len(self._players), 'maxPlayerCount':str(self.MAX_PLAYERS)}) for playerElem in self._players if playerElem != player]
        )

    # Add player to room
    # Fails if is already in or if room is full
    async def addPlayer(self, username, action, bot):
        player = PlayersManager.queryPlayer(username)
        # do nothing if the player is already in the room
        if (player in self._players):
            await player.sendMessage(bot, "AlreadyInRoom", **{'action':action})
            return False
        if len(self._players) == Room.MAX_PLAYERS:
            await player.sendMessage(bot, "RoomFull", **{'action':action})
            return False
        if (not player.isFree()):
            await player.sendMessage(bot, "InGame", **{'action':action})
            return False
        if (self._state == 1):
            await player.sendMessage(bot, "GameInProgress")
            return False

        # Add player to room
        self._players.append(player)
        player.joinRoom(self._code)
        await self.__sendRoomMessages(bot, player)
        return True

    # Remove player from room
    # Fails if not in room 
    async def removePlayer(self, player):
        if player not in self._players:
            return False
        
        # if last player, delete the room
        if len(self._players) == 1:
            return None
        if player == self._host:
            # if player is the host, make the next player the host
            self._host = self._players[1]
            return True
        self._players.remove(player)
        return True

    def hasPlayer(self, player):
        return player in self._players
    
    def joinState(self):
        return self._state == 0
    
    # WIP this this will enable the features for audience to join
    def acceptingAudience(self):
        return self._state == 1 
    
    def startGame(self):
        self._state = 1
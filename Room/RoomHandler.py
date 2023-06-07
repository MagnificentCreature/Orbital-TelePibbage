'''
Singleton class that generates, deletes and holds data about rooms
Information passed into rooms are given only as the usernames
So keeping track of who is in which room is important, and each player can only be in one room at a time
'''

import random

from Room.Room import Room

# import sys
# from pathlib import Path
# sys.path.insert(1, str(Path(__file__).parent.parent.absolute()))
from Player.PlayersManager import PlayersManager

class RoomHandler:
    #hashset of rooms by their room code
    _rooms = {}

   #Static method that generates a random four alphabet room code
    @staticmethod
    def generateRoomCode():
        code = ""
        for i in range(4):
            #randomly choose between Capital letters A-Z
            code += chr(random.randint(65, 90))
        return code
    
    #method that deletes a room
    @classmethod
    def deleteRoom(cls, room):
        del cls._rooms[room.getCode()]

    @classmethod
    async def leaveRoom(cls, player, bot):
        roomCode = await player.leaveRoom(bot)
        room = cls._rooms[roomCode]
        result = await room.removePlayer(player)
        if result is None:
            cls.deleteRoom(room)

    @classmethod
    async def joinRoom(cls, username, roomCode, bot, action="join"):
        player = PlayersManager.queryPlayer(username)
        #check if room exists
        if roomCode not in cls._rooms:
            await player.sendMessage(bot, "RoomNotFound")
            return False
        room = cls._rooms[roomCode]

        #check if player is already in a room
        if player.inRoom():
            await cls.leaveRoom(player, bot)
        await room.addPlayer(player, action, bot)
        return True

    @classmethod
    async def generateRoom(cls, username, bot):
        player = PlayersManager.queryPlayer(username)
        #keep generating room codes while making sure there is no duplicate room codes
        code = cls.generateRoomCode()
        while code in cls._rooms:
            code = cls.generateRoomCode()

        #create room and add to rooms list
        room = Room(code, player)
        cls._rooms[code] = room

        #add host to room
        if not await cls.joinRoom(username, code, bot, "create"):
            await player.sendMessage(bot, "RoomCreationFailed")
            return False

        return True
    
    @classmethod
    async def startGame(cls, username, bot):
        player = PlayersManager.queryPlayer(username)
        roomCode = player.getRoomCode()

        #check if player is in a room
        if roomCode is "":
            print("Player is not in a room, this could be a bug")
            return
        
        room = cls._rooms[roomCode]
        #check if player is host
        if not room.isHost(player):
            await player.sendMessage(bot, "NotHost")
            return
        
        #check if room has min players
        if not room.hasMinPlayers():
            await player.sendMessage(bot, "NotEnoughPlayers")
            return
        
        await room.startGame(bot)
        player.sendMessage(bot, "GameStarted")


    
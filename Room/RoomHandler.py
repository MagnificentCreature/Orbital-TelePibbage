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
from Chat.DialogueReader import DialogueReader
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

    async def leaveRoom(player, bot):
        roomCode = await player.leaveRoom(bot)
        room = RoomHandler._rooms[roomCode]
        result = await room.removePlayer(player)
        if result is None:
            RoomHandler.deleteRoom(room)

    async def joinRoom(username, roomCode, bot, action="join"):
        player = PlayersManager.queryPlayer(username)
        #check if room exists
        if roomCode not in RoomHandler._rooms:
            await player.sendMessage(bot, "RoomNotFound")
            return False
        room = RoomHandler._rooms[roomCode]

        #check if player is already in a room
        if player.inRoom():
            await RoomHandler.leaveRoom(player, bot)
        await room.addPlayer(username, action, bot)
        return True

    async def generateRoom(username, bot):
        player = PlayersManager.queryPlayer(username)
        #keep generating room codes while making sure there is no duplicate room codes
        code = RoomHandler.generateRoomCode()
        while code in RoomHandler._rooms:
            code = RoomHandler.generateRoomCode()

        #create room and add to rooms list
        room = Room(code, player)
        RoomHandler._rooms[code] = room

        #add host to room
        if not await RoomHandler.joinRoom(username, code, bot, "create"):
            await player.sendMessage(bot, "RoomCreationFailed")
            return False
        
        # if not await room.addPlayer(username, "create", bot):
        #     await player.sendMessage(bot, "RoomCreationFailed")
        #     return False
        
        return True

    
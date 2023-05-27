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
    rooms = {}

   #Static method that generates a random four alphabet room code
    @staticmethod
    def generateRoomCode():
        code = ""
        for i in range(4):
            #randomly choose between Capital letters A-Z
            code += chr(random.randint(65, 90))
        return code

    async def generateRoom(username, bot):
        player = PlayersManager.queryPlayer(username)
        #keep generating room codes while making sure there is no duplicate room codes
        code = RoomHandler.generateRoomCode()
        while code in RoomHandler.rooms:
            code = RoomHandler.generateRoomCode()

        #create room and add to rooms list
        room = Room(code, player)
        RoomHandler.rooms[code] = room

        #add host to room
        if not await room.addPlayer(username, "create", bot):
            await player.sendMessage(bot, "RoomCreationFailed")
            return False
        
        return True
    
    async def joinRoom(username, roomCode, bot):
        player = PlayersManager.queryPlayer(username)
        #check if room exists
        if roomCode not in RoomHandler.rooms:
            await player.sendMessage(bot, "RoomNotFound")
            return False
        room = RoomHandler.rooms[roomCode]
        await room.addPlayer(username, "join", bot)
        return True

    #method that deletes a room
    def deleteRoom(room):
        del RoomHandler.rooms[room.getCode()]

    
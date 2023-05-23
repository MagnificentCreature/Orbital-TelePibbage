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

    async def generateRoom(username, bot, update):
        host = PlayersManager.getPlayer(username)

        # first check if host player is already in a room
        if host.isInRoom():
            await DialogueReader.sendMessage(bot, update, "CreateRoomError")
            return None #TODO return error code for bot to print if it failed (with reason)
        # By right the code should not even reach this point because the bot would 
        # not have even register the /create_game command if the player is already in a game

        #keep generating room codes while making sure there is no duplicate room codes
        code = RoomHandler.generateRoomCode()
        while code in RoomHandler.rooms:
            code = RoomHandler.generateRoomCode()

        #create room and add to rooms
        room = Room(code, host)
        #add host to room
        room.addPlayer(host)
        
        #send join room message
        await RoomHandler.sendRoomMessages(room, bot, update)
            
        RoomHandler.rooms[code] = room
        return Room(code, host)
    
    async def joinRoom(username, roomCode, bot, update):
        return

    async def sendRoomMessages(room, bot, update):
        await DialogueReader.sendMessage(bot, update, "RoomCode", **{'roomCode':room.getCode()})
        await DialogueReader.sendMessage(bot, update, "Invite", **{'roomCode':room.getCode()})
        await DialogueReader.sendMessage(bot, update, "WaitingToStart")

    #method that deletes a room
    def deleteRoom(room):
        del RoomHandler.rooms[room.getCode()]

    
'''
Singleton class that generates, deletes and holds data about rooms
Information passed into rooms are given only as the usernames
So keeping track of who is in which room is important, and each player can only be in one room at a time
'''

import asyncio
import random
from GameController import Prompting
from BotController import BotInitiator
import Player

from Room.Room import Room

# import sys
# from pathlib import Path
# sys.path.insert(1, str(Path(__file__).parent.parent.absolute()))
from Player.PlayersManager import PlayersManager

class RoomHandler:
    #hashset of rooms by their room code
    _rooms = {}
    _updateList = []

   #Static method that generates a random four alphabet room code
    @staticmethod
    def generateRoomCode():
        code = ""
        for i in range(4):
            #randomly choose between Capital letters A-Z
            code += chr(random.randint(65, 90))
        return code
    
    @classmethod
    def getRoom(cls, roomCode):
        return cls._rooms[roomCode]
    
    #method that deletes a room
    @classmethod
    def deleteRoom(cls, room):
        del cls._rooms[room.getCode()]

    @classmethod
    async def leaveRoom(cls, username, bot):
        player = PlayersManager.queryPlayer(username)
        roomCode = await player.leaveRoom(bot)
        if roomCode is None:
            return
        room = cls._rooms[roomCode]
        result = await room.removePlayer(player)
        if result is None:
            cls.deleteRoom(room)

    @classmethod
    async def joinRoom(cls, username, roomCode, bot):
        player = PlayersManager.queryPlayer(username)
        #check if room exists
        if roomCode not in cls._rooms:
            return False
        room = cls._rooms[roomCode]

        #check if player is already in a room
        if player.inRoom():
            await cls.leaveRoom(username, bot)
        
        #add player to room
        success = await room.addPlayer(player, "join", bot)
        if not success:
            return False
        
        #send start game message to player
        await player.sendMessage(bot, "WaitingToStart", messageKey="waiting_to_start", reply_markup=BotInitiator.WaitingKeyboard)

        return True

    @classmethod
    async def generateRoom(cls, username, bot):
        host = PlayersManager.queryPlayer(username)
        #keep generating room codes while making sure there is no duplicate room codes
        roomCode = cls.generateRoomCode()
        while roomCode in cls._rooms:
            roomCode = cls.generateRoomCode()

        #create room and add to rooms list
        room = Room(roomCode, host)
        cls._rooms[roomCode] = room

        #add host to room
        if not await room.addPlayer(host, "create", bot):
            await host.sendMessage(bot, "RoomCreationFailed")
            return False
        
        # send start game message to host
        await host.sendMessage(bot, "StartGameOption", messageKey="start_game_option", reply_markup=BotInitiator.StartGameKeyboard)
        
        return True
    
    @classmethod
    async def startGame(cls, username, bot):
        player = PlayersManager.queryPlayer(username)
        roomCode = player.getRoomCode()

        #check if player is in a room
        if roomCode == "":
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

    @classmethod
    def checkState(cls, roomCode, state):
        return cls._rooms[roomCode].checkState(state)

    @classmethod
    def checkItems(cls, roomCode, item, bot):
        return cls._rooms[roomCode].checkItems(item, bot)
    
    # @classmethod
    # def setAllUserDataPhase(cls, username, phase):
    #     player = PlayersManager.queryPlayer(username)

    #     # player.setPhase(phase)
    #     # #for testing
    #     # print(username + " " + str(player.getPhase()))

    #     roomCode = player.getRoomCode()
    #     room = cls._rooms[roomCode]

    #     room.setAllUserDataPhase(phase)
    
    # @classmethod
    # def allTakePrompt(cls, username, update):
    #     player = PlayersManager.queryPlayer(username)
    #     roomCode = player.getRoomCode()
    #     room = cls._rooms[roomCode]
    #     room.allTakePrompt()
        # cls._updateList.append(update)

    # @classmethod
    # def test(cls, username):
    #     player = PlayersManager.queryPlayer(username)
    #     roomCode = player.getRoomCode()
    #     room = cls._rooms[roomCode]
    #     room.returnPlayerList()

    
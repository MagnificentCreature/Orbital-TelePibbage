'''
Singleton class that generates, deletes and holds data about rooms
Information passed into rooms are given only as the usernames
So keeping track of who is in which room is important, and each player can only be in one room at a time
'''

import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from BotController.BotInitiatorConstants import BotInitiatorConstants
from Chat.DialogueReader import DialogueReader
from GameController import Caption, Lying

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
        await player.sendMessage(bot, "WaitingToStart", messageKey="waiting_to_start", reply_markup=BotInitiatorConstants.WaitingKeyboard, parse_mode=DialogueReader.MARKDOWN, **{'gameMode':room.getMode().value})
        
        return True

    @classmethod
    async def generateRoom(cls, username, bot, roomCode=None):
        host = PlayersManager.queryPlayer(username)
        #keep generating room codes while making sure there is no duplicate room codes
        if roomCode is None:
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
        
        # send start game message to 
        keyboard = BotInitiatorConstants.StartGameButtons.copy()
        keyboard[1][0] = InlineKeyboardButton(text=f"Change to Arcade Game Mode", callback_data=str(BotInitiatorConstants.CHANGE_MODE))
        await host.sendMessage(bot, "StartGameOption", messageKey="start_game_option", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=DialogueReader.MARKDOWN, **{'gameMode':room.getMode().value})
        
        return True
    
    @classmethod
    async def changeMode(cls, username, bot):
        player = PlayersManager.queryPlayer(username)
        roomCode = player.getRoomCode()
        
        #check if player is in a room
        if roomCode == "":
            print("Player is not in a room, this could be a bug")
            return False
        
        room = cls._rooms[roomCode]
        #check if player is host
        if not room.isHost(player):
            await player.sendMessage(bot, "NotHost")
            return False
        
        return await room.changeMode()

    @classmethod
    async def startGame(cls, username, bot):
        player = PlayersManager.queryPlayer(username)
        roomCode = player.getRoomCode()

        #check if player is in a room
        if roomCode == "":
            print("Player is not in a room, this could be a bug")
            return False
        
        room = cls._rooms[roomCode]
        #check if player is host
        if not room.isHost(player):
            await player.sendMessage(bot, "NotHost")
            return False
        
        #check if room has min players
        if not room.hasMinPlayers():
            await player.sendMessage(bot, "NotEnoughPlayers")
            return False
        
        return await room.startGame(bot)

    @classmethod
    def checkState(cls, roomCode, state):
        return cls._rooms[roomCode].checkState(state)

    @classmethod
    def checkItems(cls, roomCode, item, bot):
        return cls._rooms[roomCode].checkItems(item, bot)
    
    @classmethod
    def getRoom(cls, roomCode):
        return cls._rooms[roomCode]  
    
    @classmethod
    def getGameMode(cls, roomCode):
        return cls._rooms[roomCode].getMode()
    
    '''
    Prompting Phase methods
    '''
    @classmethod
    async def takeImage(cls, roomCode, username, image):
        player = PlayersManager.queryPlayer(username)
        await cls._rooms[roomCode].takeImage(player, image)

    '''
    Lying Phase Methods
    '''
    @classmethod
    async def sendNextImage(cls, bot, roomCode, username):
        player = PlayersManager.queryPlayer(username)
        if cls._rooms[roomCode].getMode() == Room.Mode.VANILLA:
            return await Lying.sendNextImage(bot, cls._rooms[roomCode], player)
        elif cls._rooms[roomCode].getMode() == Room.Mode.ARCADE:
            return await Caption.sendNextImage(bot, cls._rooms[roomCode], player)

    '''
    End game methods
    '''
    @classmethod
    async def endGame(cls, roomCode, bot):
        await cls._rooms[roomCode].endGame(bot)
        del cls._rooms[roomCode]
        return True
    
    @classmethod
    async def playAgain(cls, bot, username, oldRoomCode):
        if oldRoomCode not in cls._rooms:
            await cls.generateRoom(username, bot, oldRoomCode)
        else:
            await cls.joinRoom(username, oldRoomCode, bot)
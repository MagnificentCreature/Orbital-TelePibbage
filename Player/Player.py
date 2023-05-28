'''
Player object, identified by his unique username.
Stores information about his username, scores etc
Can later be linked to a database to keep track of (leaderboard/overall scores)
'''

from Chat.DialogueReader import DialogueReader


class Player:
    username = ""
    _chatID = 0
    score = 0
    inGame = False
    roomCode = ""
    
    def __init__(self, username, chatID=0, score=0):
        self.username = username
        self._chatID = chatID
        self.score = score
        self.inGame = False
        self.roomCode = ""
        
    def isFree(self):
        return not self.inGame
    
    def isHost(self):
        return False
    
    def getScore(self):
        return self.score
    
    def getUsername(self):
        return self.username
    
    def inRoom(self):
        return self.roomCode != ""
    
    def joinRoom(self, roomCode):
        self.roomCode = roomCode

    async def leaveRoom(self, bot):
        await self.sendMessage(bot, "LeavingRoom", **{'roomCode':self.roomCode})
        tempRoomCode = self.roomCode
        self.roomCode = None
        return tempRoomCode
    
    async def sendMessage(self, bot, message):
        await DialogueReader.sendMessageByID(bot, self._chatID, message)

    async def sendMessage(self, bot, message, **kwargs):
        await DialogueReader.sendMessageByID(bot, self._chatID, message, **kwargs)
        
    async def sendImageURL(self, bot, imageURL):
        await DialogueReader.sendImageURLByID(bot, self._chatID, imageURL)
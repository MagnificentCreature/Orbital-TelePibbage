'''
Player object, identified by his unique username.
Stores information about his username, scores etc
Can later be linked to a database to keep track of (leaderboard/overall scores)
'''

from Chat.DialogueReader import DialogueReader


class Player:
    _username = ""
    _chatID = 0
    _score = 0
    _inGame = False
    _roomCode = ""
    _userCtx = None
    
    def __init__(self, username, chatID=0, _userCtx=None, score=0):
        self._username = username
        self._chatID = chatID
        self._score = score
        self._inGame = False
        self._roomCode = ""
        self._userCtx = _userCtx
        
    def isFree(self):
        return not self._inGame
    
    def isHost(self):
        return False
    
    def getScore(self):
        return self._score
    
    def getUsername(self):
        return self._username
    
    def inRoom(self):
        return self._roomCode != ""
    
    def joinRoom(self, roomCode):
        self._roomCode = roomCode

    async def leaveRoom(self, bot):
        await self.sendMessage(bot, "LeavingRoom", **{'roomCode':self._roomCode})
        tempRoomCode = self._roomCode
        self._roomCode = None
        return tempRoomCode
    
    async def sendMessage(self, bot, message):
        await DialogueReader.sendMessageByID(bot, self._chatID, message)

    async def sendMessage(self, bot, message, **kwargs):
        await DialogueReader.sendMessageByID(bot, self._chatID, message, **kwargs)
        
    async def sendImageURL(self, bot, imageURL):
        await DialogueReader.sendImageURLByID(bot, self._chatID, imageURL)
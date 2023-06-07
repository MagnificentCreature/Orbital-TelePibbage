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
    _userCtx = None
    
    def __init__(self, username, chatID=0, _userCtx=None, score=0):
        self._username = username
        self._chatID = chatID
        self._score = score
        self._userCtx = _userCtx
        _userCtx.user_data['in_game'] = False
        _userCtx.user_data['roomCode'] = ""
        
    def __getRoomCode(self):
        return self._userCtx.user_data['roomCode']

    def isFree(self):
        return not self.user_data['in_game']
    
    def isHost(self):
        return False
    
    def getScore(self):
        return self._score
    
    def getUsername(self):
        return self._username
    
    def inRoom(self):
        return self._userCtx.user_data['roomCode'] != ""
    
    def joinRoom(self, roomCode):
        self._userCtx.user_data['roomCode'] = roomCode

    async def leaveRoom(self, bot):
        await self.sendMessage(bot, "LeavingRoom", **{'roomCode':self._roomCode})
        tempRoomCode = self.__getRoomCode()
        self._userCtx.user_data['roomCode'] = ""
        return tempRoomCode
    
    async def startGame(self, bot):
        await self.sendMessage(bot, "StartingGame")
        self._userCtx.user_data['waiting_to_start'].set()
        self._userCtx.user_data['in_game'] = True
    
    async def sendMessage(self, bot, message):
        await DialogueReader.sendMessageByID(bot, self._chatID, message)

    async def sendMessage(self, bot, message, **kwargs):
        await DialogueReader.sendMessageByID(bot, self._chatID, message, **kwargs)
        
    async def sendImageURL(self, bot, imageURL):
        await DialogueReader.sendImageURLByID(bot, self._chatID, imageURL)
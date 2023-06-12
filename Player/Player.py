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
    _user_data = None
    
    def __init__(self, username, chatID=0, _user_data={}, score=0):
        self._username = username
        self._chatID = chatID
        self._score = score
        self._user_data = _user_data
        _user_data['in_game'] = False
        _user_data['roomCode'] = ""
        
    def updateUserData(self, _user_data):
        self._user_data = _user_data
        _user_data['in_game'] = False
        _user_data['roomCode'] = ""

    def getRoomCode(self):
        return self._user_data['roomCode']

    def isFree(self):
        return not self._user_data['in_game']
    
    def getScore(self):
        return self._score
    
    def getUsername(self):
        return self._username
    
    def inRoom(self):
        return self._user_data['roomCode'] != ""
    
    def joinRoom(self, roomCode):
        self._user_data['roomCode'] = roomCode

    async def leaveRoom(self, bot):
        if self._user_data['roomCode'] == "":
            return
        await self.sendMessage(bot, "LeavingRoom", **{'roomCode':self.getRoomCode()})
        tempRoomCode = self.getRoomCode()
        self._user_data['roomCode'] = ""
        return tempRoomCode
    
    def setInGame(self):
        self._user_data['in_game'] = True

    async def startGame(self):
        self._user_data['waiting_to_start'].set()
        self.setInGame()
    
    async def sendMessage(self, bot, message, reply_markup=None):
        await DialogueReader.sendMessageByID(bot, self._chatID, message, reply_markup=reply_markup)

    async def sendMessage(self, bot, message, reply_markup=None, **kwargs):
        await DialogueReader.sendMessageByID(bot, self._chatID, message, reply_markup=reply_markup, **kwargs)
        
    async def sendImageURL(self, bot, imageURL):
        await DialogueReader.sendImageURLByID(bot, self._chatID, imageURL)
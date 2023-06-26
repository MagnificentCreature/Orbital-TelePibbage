'''
Player object, identified by his unique username.
Stores information about his username, scores etc
Can later be linked to a database to keep track of (leaderboard/overall scores)
'''
from enum import Enum

from Chat.DialogueReader import DialogueReader
from telegram import InputMediaPhoto

class Player:
    _username = ""
    _chatID = 0
    _score = 0
    _user_data = None
    
    class PlayerConstants(Enum):
        PROMPT = "prompt"
        LIE = "lie"
        NEXT_LIE = "next_lie"
        HAS_VOTED = "has_voted"
    
    def __init__(self, username, chatID=0, _user_data={}, score=0, sentPrompt=False):
        self._username = username
        self._chatID = chatID
        self._score = score
        self._user_data = _user_data
        _user_data['in_game'] = False
        _user_data['roomCode'] = ""

    def __str__(self):
        return self._username
                
    def reset(self):
        for itemKey in self.PlayerConstants.__members__.values():
            try:
                del self._user_data[itemKey.value]
            except KeyError:
                continue
        self._user_data['in_game'] = False
        self._user_data['roomCode'] = ""
        self._score = 0


    def updateUserData(self, _user_data):
        # Initialise the user data
        # TODO make this a factory method
        self._user_data = _user_data
        _user_data['in_game'] = False
        _user_data['roomCode'] = ""

    def getRoomCode(self):
        return self._user_data['roomCode']

    def isFree(self):
        return not self._user_data['in_game']
    
    def getScore(self):
        return self._score
    
    def addScore(self, points):
        self._score += points
    
    def getUsername(self):
        return self._username

    def getChatID(self):
        return self._chatID
    
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

    # def setPhase(self, phase):
    #     self._user_data['phase'] = phase

    # def queryPhase(self, phase):
    #     return self._user_data['phase'] == phase
    
    def setInGame(self):
        self._user_data['in_game'] = True
    
    def setItem(self, itemKey, value):
        print("Setting item " + str(itemKey) + " to " + str(value))
        if itemKey not in Player.PlayerConstants.__members__.values():
            return False
        self._user_data[itemKey.value] = value

    def querySentItem(self, itemKey):
        if itemKey not in Player.PlayerConstants.__members__.values():
            return False
        try:
            return self._user_data[itemKey.value] is not None and self._user_data[itemKey.value] is not False
        except KeyError:
            return False
    
    async def startGame(self):
        self.deleteContext('lobby_list')
        self.setInGame()

    def deleteContext(self, key):
        try:
            del self._user_data[key]
        except KeyError:
            del self._user_data[key.value]

    async def queryMessagekey(self, messageKey):
        try:
            return self._user_data[messageKey] is not None
        except KeyError:
            return False

    # Methods to send messages
    async def editMessage(self, messageKey, message, newMessageKey=None, reply_markup=None):
        await self._user_data[messageKey].edit_text(text=DialogueReader.queryDialogue(message), reply_markup=reply_markup)
        if newMessageKey != None:
            self._user_data[newMessageKey] = self._user_data.pop(messageKey)


    async def editMessage(self, messageKey, message, newMessageKey=None, reply_markup=None, **kwargs):
        await self._user_data[messageKey].edit_text(text=DialogueReader.queryDialogue(message, **kwargs), reply_markup=reply_markup)
        if newMessageKey != None:
            self._user_data[newMessageKey] = self._user_data.pop(messageKey)

    async def editImageURL(self, messageKey, imageURL, newMessageKey=None, reply_markup=None):
        await self._user_data[messageKey].edit_media(media=InputMediaPhoto(imageURL), reply_markup=reply_markup)
        if newMessageKey != None:
            self._user_data[newMessageKey] = self._user_data.pop(messageKey)

    async def deleteMessage(self, messageKey):
        await self._user_data[messageKey].delete()
        del self._user_data[messageKey]

    # Including a message key will store the message's ID in the user_data which can be editted later
    async def sendMessage(self, bot, message, messageKey=None, reply_markup=None, raw=False):
        messasgeID = await DialogueReader.sendMessageByID(bot, self._chatID, message, raw=raw, reply_markup=reply_markup)
        if messageKey != None:
            self._user_data[messageKey] = messasgeID

    async def sendMessage(self, bot, message, messageKey=None, reply_markup=None, raw=False, **kwargs):
        messasgeID = await DialogueReader.sendMessageByID(bot, self._chatID, message, reply_markup=reply_markup, raw=raw, **kwargs)
        if messageKey != None:
            self._user_data[messageKey] = messasgeID
        
    async def sendImageURL(self, bot, imageURL, messageKey=None, reply_markup=None):
        messasgeID = await DialogueReader.sendImageURLByID(bot, self._chatID, imageURL, reply_markup=reply_markup)
        if messageKey != None:
            self._user_data[messageKey] = messasgeID
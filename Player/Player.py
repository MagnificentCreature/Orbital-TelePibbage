'''
Player object, identified by his unique username.
Stores information about his username, scores etc
Can later be linked to a database to keep track of (leaderboard/overall scores)
'''
import asyncio
from enum import Enum

import telegram

from Chat.DialogueReader import DialogueReader
from telegram import InputMediaPhoto

from Player.PlayerConstants import PlayerConstants

class Player:
    _username = ""
    _chatID = 0
    _score = 0
    _user_data = None
    _running_edit = False
    
    def timeOutRetryDecorator(func):
        async def wrapper(*args, **kwargs):
            max_retries = 5
            retry_delay = 1
            retry_count = 0
            while retry_count < max_retries:
                try:
                    return await func(*args, **kwargs)
                except telegram.error.TimedOut as e:
                    if retry_count >= max_retries:
                        print(f"Timed out: {str(e)} after {retry_count} retries. Giving up.")
                        raise
                    else:
                        print(f"Timed out: {str(e)} running {func.__name__}. Retrying in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2
                        retry_count += 1

            return await wrapper(*args, **kwargs)
        return wrapper
    
    def __init__(self, username, chatID=0, _user_data={}, score=0):
        self._username = username
        self._chatID = chatID
        self._score = score
        self._user_data = _user_data
        _user_data['in_game'] = False
        _user_data['roomCode'] = ""

    def __str__(self):
        return self._username
                
    def reset(self):
        for itemKey in PlayerConstants.__members__.values():
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
        if itemKey not in PlayerConstants.__members__.values():
            return False
        self._user_data[itemKey.value] = value

    def queryItem(self, itemKey):
        if itemKey not in PlayerConstants.__members__.values() or itemKey.value not in self._user_data:
            return False
        try:
            if self._user_data[itemKey.value] is not None and self._user_data[itemKey.value] is not False:
                return self._user_data[itemKey.value]
        except KeyError:
            print(f"itemKey {itemKey.value} returned KeyError, likely inputted string instead of player constant")
            return False
    
    async def startGame(self):
        self.deleteContext('lobby_list')
        self.setInGame()

    def deleteContext(self, key):
        try:
            if key in self._user_data:
                del self._user_data[key]
            else:
                del self._user_data[key.value]
        except (KeyError, AttributeError) as error:
            pass

    async def queryMessagekey(self, messageKey):
        try:
            return self._user_data[messageKey] is not None
        except KeyError:
            return False

    # Methods to send messages
    # async def editMessage(self, messageKey, message, newMessageKey=None, reply_markup=None, parse_mode=None):
    #     await self._user_data[messageKey].edit_text(text=DialogueReader.queryDialogue(message), reply_markup=reply_markup, parse_mode=parse_mode)
    #     if newMessageKey != None:
    #         self._user_data[newMessageKey] = self._user_data.pop(messageKey)

    @timeOutRetryDecorator
    async def editMessage(self, messageKey, message, newMessageKey=None, reply_markup=None, parse_mode=None, **kwargs):
        if messageKey not in self._user_data:
            return
        try:
            await self._user_data[messageKey].edit_text(text=DialogueReader.queryDialogue(message, **kwargs), reply_markup=reply_markup, parse_mode=parse_mode)
        except telegram.error.BadRequest as badReqError:
            print(badReqError)
            pass
        if newMessageKey != None:
            self._user_data[newMessageKey] = self._user_data.pop(messageKey)

    @timeOutRetryDecorator
    async def editImageURL(self, messageKey, imageURL, newMessageKey=None, reply_markup=None, parse_mode=None, caption=None, **kwargs):
        await self._user_data[messageKey].edit_media(media=InputMediaPhoto(imageURL, caption=DialogueReader.queryDialogue(caption, **kwargs), parse_mode=parse_mode), reply_markup=reply_markup)
        if newMessageKey != None:
            self._user_data[newMessageKey] = self._user_data.pop(messageKey)

    async def deleteMessage(self, messageKey, itemKey=None):
        if messageKey not in self._user_data:
            return
        # Item key is used if the messageKey is a dictionary or list of messages
        if itemKey != None:
            await self._user_data[messageKey][itemKey].delete()
            try:
                del self._user_data[messageKey][itemKey]
            except TypeError:
                pass
            return
        try:
            await self._user_data[messageKey].delete()
        except telegram.error.BadRequest as badReqError:
            print(badReqError)
            pass
        try:
            del self._user_data[messageKey]
        except KeyError:
            pass

    @timeOutRetryDecorator
    async def deleteMessageList(self, messageKeyList):
        if messageKeyList not in self._user_data:
            return
        try:
            for message in self._user_data[messageKeyList]:
                try:
                    await message.delete()
                except telegram.error.BadRequest as badReqError:
                    pass
        except TypeError:
            pass
        del self._user_data[messageKeyList]

    # # Including a message key will store the message's ID in the user_data which can be editted later
    # async def sendMessage(self, bot, message, messageKey=None, reply_markup=None, raw=False):
    #     messasgeID = await DialogueReader.sendMessageByID(bot, self._chatID, message, raw=raw, reply_markup=reply_markup)
    #     if messageKey != None:
    #         self._user_data[messageKey] = messasgeID

    async def sendMessage(self, bot, message, messageKey=None, reply_markup=None, raw=False, parse_mode=None, **kwargs):
        messasgeID = await DialogueReader.sendMessageByID(bot, self._chatID, message, reply_markup=reply_markup, raw=raw, parse_mode=parse_mode, **kwargs)
        if messageKey != None:
            self._user_data[messageKey] = messasgeID
        
    async def sendImageURL(self, bot, imageURL, messageKey=None, reply_markup=None, caption=None, raw=False, parse_mode=None, **kwargs):
        messasgeID = await DialogueReader.sendImageURLByID(bot, self._chatID, imageURL, caption=caption, raw=raw, parse_mode=parse_mode, reply_markup=reply_markup, **kwargs)
        if messageKey != None:
            self._user_data[messageKey] = messasgeID
    async def sendMediaGroup(self, bot, mediaGroup, messageKey=None, caption=None, raw=False, parse_mode=None, **kwargs):
        # Note messageID will be a list of message IDs for each media
        messasgeIDs = await DialogueReader.sendMediaGroupByID(bot, self._chatID, mediaGroup, caption=caption, raw=raw, parse_mode=parse_mode, **kwargs)
        if messageKey != None:
            self._user_data[messageKey] = messasgeIDs
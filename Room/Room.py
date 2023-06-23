"""
Class that holds data about rooms
"""
from enum import Enum
import asyncio
from collections import deque
from BotController import BotInitiator
from GameController import Prompting, Lying, Voting#,  Reveal
from GameController.Image import Image
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update

class Room:
    _code = ""
    _host = None #player object
    _players = [] #contains list of player objects
    MAX_PLAYERS = 8
    MIN_PLAYERS = 2
    _state = 0 # 0 = join state, 1 = game state
    _list_of_images = []
    _list_copy = None
    _current_voting_image = None

    # _list_of_images = [
    #     Image("Author 1", "Prompt 1", "https://example.com/image1.jpg"),
    #     Image("Author 2", "Prompt 2", "https://example.com/image2.jpg"),
    #     Image("Author 3", "Prompt 3", "https://example.com/image3.jpg")
    # ]

    # # Insert some sample lies for testing
    # _list_of_images[0].insertLie("Lie 1 by Player 1", "Player 1")
    # _list_of_images[0].insertLie("Lie 2 by Player 2", "Player 2")
    # _list_of_images[1].insertLie("Lie 3 by Player 1", "Player 1")
    # _list_of_images[2].insertLie("Lie 4 by Player 2", "Player 2")

    _playerToRemainingImages = {} #dictionary of player to list of images they have yet to give lies for
    
    class State(Enum):
        JOIN_STATE, PROMPTING_STATE, LYING_STATE, VOTING_STATE, REVEAL_STATE = range(5)

    def __init__(self, code, host):
        self._code = code
        self._host = host
        self._players = []
        self._state = Room.State.JOIN_STATE

    def getCode(self):
        return self._code
    
    def hasPlayer(self, player):
        return player in self._players
    
    def joinState(self):
        return self._state == Room.State.JOIN_STATE
    
    def isHost(self, player):
        return player == self._host
    
    def hasMinPlayers(self):
        return len(self._players) >= Room.MIN_PLAYERS
    
    async def broadcast(self, bot, message, messageKey=None,reply_markup=None, **kwargs):
        for player in self._players:
            await player.sendMessage(bot, message, messageKey, reply_markup, **kwargs)

    async def broadCall(self, bot, func):
        for player in self._players:
            await func(bot, self, player)

    # Return a string of the players usernames in a list format
    def printPlayerList(self):
        s = ""
        for player in self._players:
            s += "\n@" + player.getUsername()
            if player == self._host: 
                s += " (Host)"
        return s

    # Dialogue messages to send when adding player
    async def __joinRoomMessages(self, bot, player):
        await player.sendMessage(bot, "RoomCode", **{'roomCode':self.getCode()})
        await player.sendMessage(bot, "Invite", **{'roomCode':self.getCode()})
        # send message to player
        await player.sendMessage(bot, "LobbyList", messageKey="lobby_list", **{'playerCount':len(self._players), 'maxPlayerCount':str(self.MAX_PLAYERS), 'lobbyList':self.printPlayerList()})
        # edit everyones messages
        await asyncio.gather(
            *[playerElem.editMessage("lobby_list", "LobbyList", **{'playerCount':len(self._players), 'maxPlayerCount':str(self.MAX_PLAYERS), 'lobbyList':self.printPlayerList()}) for playerElem in self._players if playerElem != player]
        )

    async def __leaveRoomMessages(self):
        # Update everyone elses lobby list
        await asyncio.gather(
            *[playerElem.editMessage("lobby_list", "LobbyList", **{'playerCount':len(self._players), 'maxPlayerCount':str(self.MAX_PLAYERS), 'lobbyList':self.printPlayerList()}) for playerElem in self._players]
        )

    async def checkState(self, state):
        return self._state == state

    # Add player to room
    # Fails if is already in or if room is full
    async def addPlayer(self, player, action, bot):
        # do nothing if the player is already in the room
        if (player in self._players):
            await player.sendMessage(bot, "AlreadyInRoom", **{'action':action})
            return False
        if len(self._players) == Room.MAX_PLAYERS:
            await player.sendMessage(bot, "RoomFull", **{'action':action})
            return False
        if (not player.isFree()):
            await player.sendMessage(bot, "InGame", **{'action':action})
            return False
        if (self._state != Room.State.JOIN_STATE):
            await player.sendMessage(bot, "GameInProgress")
            return False

        # Add player to room
        self._players.append(player)
        player.joinRoom(self._code)
        await self.__joinRoomMessages(bot, player)
        return True

    # Remove player from room
    # Fails if not in room 
    async def removePlayer(self, player):
        if player not in self._players:
            return False
        
        # if last player, delete the room
        if len(self._players) == 1:
            return None
        if player == self._host:
            # if player is the host, make the next player the host
            self._host = self._players[1]
            # Sesnd new host the host message
            await self._host.editMessage("waiting_to_start", "StartGameOption", newMessageKey="start_game_option", reply_markup=BotInitiator.StartGameKeyboard)
        self._players.remove(player)
        await self.__leaveRoomMessages()
        return True
    
    async def advanceState(self, bot):
        match self._state:
            case Room.State.JOIN_STATE:
                await Prompting.beginPhase1(bot, self)
                self._state = Room.State.PROMPTING_STATE
            case Room.State.PROMPTING_STATE:
                await Lying.beginPhase2(bot, self)
                # TODO: Maybe delete the players usercontext['prompt']?
                self._state = Room.State.LYING_STATE
            case Room.State.LYING_STATE:
                # TODO: Maybe delete the players usercontext['lies']?
                self._list_copy = self._list_of_images.copy() # TODO: Move this into VotingPhase3
                await Voting.beginPhase3(bot, self)
                self._state = Room.State.VOTING_STATE
            case Room.State.VOTING_STATE:
                #await Reveal.beginPhase4(bot, self)
                self._state = Room.State.REVEAL_STATE
            case Room.State.REVEAL_STATE:
                print("Game Over")

    async def startGame(self, bot):
        for eachPlayer in self._players:
            self._playerToRemainingImages[eachPlayer] = []
            if eachPlayer == self._host:
                eachPlayer.setInGame()
                continue
            await eachPlayer.sendMessage(bot, "StartingGame", **{'host':self._host.getUsername()})
            await eachPlayer.startGame()
        await self.advanceState(bot)
        return True
    
    #true if all have sent prompts(or other item) and proceeded to next phase
    async def checkItems(self, item, bot, advance=True):
        for playerObj in self._players: 
            if not playerObj.querySentItem(item):
                return False
        # At this point all players have sent prompts, advance state
        if advance:
            await self.advanceState(bot)
        return True

    # WIP this this will enable the features for audience to join
    def acceptingAudience(self):
        return #self._state == 1 

    async def takeImage(self, player, image):
        if player not in self._players:
            return False
        if self._state != Room.State.PROMPTING_STATE:
            return False
        self._list_of_images.append(image)
        for eachPlayer in self._players:
            if eachPlayer == player:
                continue
            self._playerToRemainingImages[eachPlayer].append(image) 

    async def getRemainingImages(self, player):
        return self._playerToRemainingImages[player]                      

    async def broadcast_voting_image(self, bot):
        imageObj = self._list_copy.pop()
        image_url = imageObj.getImageURL()
        lie_buttons = imageObj.getInlineKeyboard()
        author = imageObj.getAuthor()
        # print('buttons '+ str(lie_buttons))

        self._current_voting_image = imageObj

        for eachPlayer in self._players:
            if eachPlayer.getUsername() == author:
                await eachPlayer.sendImageURL(bot, image_url)    
            else:
                await eachPlayer.sendImageURL(bot, image_url, reply_markup=lie_buttons)
        if len(self._list_copy) <= 0:
            return False #Return false to indicate that there are no more images to send after
        return True

    async def getVotingImage(self):
        return self._current_voting_image
 
                        

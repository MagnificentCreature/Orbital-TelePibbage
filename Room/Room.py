"""
Class that holds data about rooms
"""
from enum import Enum
import asyncio
from collections import deque
from BotController import BotInitiator
from Chat.DialogueReader import DialogueReader
from GameController import Prompting, Lying, Voting, Reveal
from GameController.Image import Image
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update

from Player.Player import Player

class Room:
    _code = ""
    _host = None #player object
    _players = [] #contains list of player objects
    MAX_PLAYERS = 8
    MIN_PLAYERS = 2
    _mode = None #game mode
    _state = 0 # 0 = join state, 1 = game state
    _list_of_images = []
    _list_copy = None
    _current_voting_image = None
    _playerToRemainingImages = {} #dictionary of player to list of images they have yet to give lies for
    
    class State(Enum):
        JOIN_STATE, PROMPTING_STATE, LYING_STATE, VOTING_STATE, REVEAL_STATE = range(5)
    class Mode(Enum):
        VANILLA, ARCADE = "Vanilla", "Arcade"

    def __init__(self, code, host):
        self._code = code
        self._host = host
        self._players = []
        self._list_of_images = []
        self._state = Room.State.JOIN_STATE
        self._mode = Room.Mode.VANILLA

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
    
    async def broadcast(self, bot, message, messageKey=None,reply_markup=None, raw=False, parse_mode=None, **kwargs):
        for player in self._players:
            await player.sendMessage(bot, message, messageKey, reply_markup, raw=raw, parse_mode=parse_mode,**kwargs)

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

    def get_other_member(self, member):
        if member == self.Mode.ARCADE:
            return self.Mode.VANILLA
        else:
            return self.Mode.ARCADE

    # Dialogue messages to send when adding player
    async def __joinRoomMessages(self, bot, player):
        await player.sendMessage(bot, "RoomCode", **{'roomCode':self.getCode()})
        # await player.sendMessage(bot, "GameMode", messageKey="game_mode", **{'gameMode':self._mode.value})
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
        
        # Send messages to player and other players
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
            # Send new host the host message
            keyboard = BotInitiator.StartGameButtons.copy()
            keyboard[0][1].text = f"Change to {self._mode.value} Game Mode"
            await self._host.editMessage("waiting_to_start", "StartGameOption", newMessageKey="start_game_option", reply_markup=InlineKeyboardMarkup(keyboard))
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
                await Reveal.beginPhase4(bot, self)
                self._state = Room.State.REVEAL_STATE
            case Room.State.REVEAL_STATE:
                return

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
    
    async def changeMode(self):
        # change _mode to the other mode
        self._mode = self.get_other_member(self._mode)
        
        # send message to all players
        for eachPlayer in self._players:
            if self.isHost(eachPlayer):
                keyboard = BotInitiator.StartGameButtons.copy()
                keyboard[1][0] = InlineKeyboardButton(text=f"Change to {self.get_other_member(self._mode).value} Game Mode", callback_data=str(BotInitiator.CHANGE_MODE))
                await eachPlayer.editMessage("start_game_option", "StartGameOption", reply_markup=InlineKeyboardMarkup(keyboard))
                continue
            await eachPlayer.editMessage("waiting_to_start", "WaitingToStart", reply_markup=BotInitiator.WaitingKeyboard, parse_mode=DialogueReader.MARKDOWN, **{'gameMode':self._mode.value})
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
        if len(self._list_copy) <= 0:
            return False 

        imageObj = self._list_copy.pop()
        image_url = imageObj.getImageURL()
        author = imageObj.getAuthor()

        self._current_voting_image = imageObj

        for eachPlayer in self._players:
            if eachPlayer.getUsername() == author:
                eachPlayer.setItem(Player.PlayerConstants.HAS_VOTED, True)
                await eachPlayer.sendImageURL(bot, image_url)    
            else:
                eachPlayer.setItem(Player.PlayerConstants.HAS_VOTED, False)
                await eachPlayer.sendImageURL(bot, image_url, reply_markup=imageObj.getInlineKeyboard(eachPlayer.getUsername()))
        # if len(self._list_copy) <= 0:
        #     return False #Return false to indicate that there are no more images to send after
        return True

    async def getVotingImage(self):
        return self._current_voting_image
    
    def getLeaderboard(self):
        leaderboard = sorted(self._players, key=lambda player: player.getScore(), reverse=True)
        message = f"*☆☆☆☆☆{leaderboard[0]}☆☆☆☆☆*\n"
        message += "*Congratulations\!\!*\n\n"

        message += "TelePibbage Leaderboard:\n"

        for i, player in enumerate(leaderboard, start=1):
            username = player.getUsername()
            score = player.getScore()
            message += f"{i}\. {username}: {score} points\n"

        return message
    
    async def endGame(self, bot):
        for player in self._players:
            player.reset()
            PlayAgainKeyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(text="Create Room", callback_data=str(BotInitiator.CREATE_ROOM)),
                    InlineKeyboardButton(text="Join Room", callback_data=str(BotInitiator.JOIN_ROOM)),
                ],
                [
                    InlineKeyboardButton(text="Play with the same people", callback_data=f"{str(BotInitiator.PLAY_AGAIN)}:{self._code}")
                ]
            ])
            await player.sendMessage(bot, "Welcome3", reply_markup=PlayAgainKeyboard)
 
                        

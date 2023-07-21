"""
Class that holds data about rooms
"""
from enum import Enum
import asyncio
from collections import deque
import random
from BotController import BotInitiator
from Chat.DialogueReader import DialogueReader
from GameController import ArcadeGen, Battle, Caption, CaptionSelection, Prompting, Lying, Voting, Reveal
from GameController.Image import Image
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update

from Player.Player import Player
from Player.PlayersManager import PlayersManager

class Room:
    _code = ""
    _host = None #player object
    _players = [] #contains list of player objects
    _shuffled_players = [] #contains list of player objects but shuffled for arcade mode
    MAX_PLAYERS = 8
    MIN_PLAYERS = 2
    _mode = None #game mode
    _state = 0 # 0 = join state, 1 = game state
    _list_of_images = []
    _list_copy = None #Copy of image list to pop for voting and for arcade battling
    _current_voting_image = None
    _playerToRemainingImages = {} #dictionary of player to list of images they have yet to give lies for
    _advancing = False #boolean to check if game is advancing to next state, for flow control
    _current_battle_images = ()
    
    class State(Enum):
        JOIN_STATE, PROMPTING_STATE, LYING_STATE, VOTING_STATE, REVEAL_STATE, ARCADE_GEN_STATE, CAPTION_STATE, CAPTION_SELECTION_STATE, BATTLE_STATE = range(9)
    class Mode(Enum):
        VANILLA, ARCADE = "Vanilla", "Arcade"

    def __init__(self, code, host):
        self._code = code
        self._host = host
        self._players = []
        self._list_of_images = []
        self._state = Room.State.JOIN_STATE
        self._mode = Room.Mode.VANILLA
        self._advancing = False
        self._shuffled_players = []

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
    
    def getMode(self):
        return self._mode
    
    async def broadcast(self, bot, message, messageKey=None, reply_markup=None, raw=False, parse_mode=None, **kwargs):
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
            await self._host.editMessage("waiting_to_start", "StartGameOption", newMessageKey="start_game_option", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=DialogueReader.MARKDOWN, **{'gameMode':self._mode.value})
        self._players.remove(player)
        await self.__leaveRoomMessages()
        return True
    
    async def advanceState(self, bot):
        for player in self._players:
            await player.deleteMessage("waiting_msg")
        if not self._advancing:
            self._advancing = True
        else:
            return
        if self._mode == Room.Mode.VANILLA:
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
                # Currently has no use
                case Room.State.REVEAL_STATE:
                    return
        elif self._mode == Room.Mode.ARCADE:
            match self._state:
                case Room.State.JOIN_STATE:
                    await ArcadeGen.beginPhase1(bot, self)
                    self._state = Room.State.ARCADE_GEN_STATE
                case Room.State.ARCADE_GEN_STATE:
                    await Caption.beginPhase2(bot, self)
                    self._state = Room.State.CAPTION_STATE
                case Room.State.CAPTION_STATE:
                    await CaptionSelection.beginPhase3(bot, self)
                    self._state = Room.State.CAPTION_SELECTION_STATE
                case Room.State.CAPTION_SELECTION_STATE:
                    await Battle.beginPhase4(bot, self)
                    self._state = Room.State.BATTLE_STATE
                # Currently has no use
                case Room.State.BATTLE_STATE:
                    return
        self._advancing = False

    async def startGame(self, bot):
        self._shuffled_players = self._players.copy()
        random.shuffle(self._shuffled_players)
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
                await eachPlayer.editMessage("start_game_option", "StartGameOption", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=DialogueReader.MARKDOWN, **{'gameMode':self._mode.value})
                continue
            await eachPlayer.editMessage("waiting_to_start", "WaitingToStart", reply_markup=BotInitiator.WaitingKeyboard, parse_mode=DialogueReader.MARKDOWN, **{'gameMode':self._mode.value})
        return True
    
    #true if all have sent prompts(or other item) and proceeded to next phase
    async def checkItems(self, item, bot, advance=True):
        for playerObj in self._players: 
            if not playerObj.queryItem(item):
                return False
        # At this point all players have sent prompts, advance state (unless in the case of lie, where we wait for players to send all their lies)
        if advance:
            await self.advanceState(bot)
        return True

    # WIP this this will enable the features for audience to join
    def acceptingAudience(self):
        return #self._state == 1 

    async def takeImage(self, player, image):
        if player not in self._players:
            return False
        if self._state != Room.State.PROMPTING_STATE and self._state != Room.State.ARCADE_GEN_STATE:
            return False
        self._list_of_images.append(image)
        if self._mode == Room.Mode.VANILLA:
            for eachPlayer in self._players:
                if eachPlayer == player:
                    continue
                self._playerToRemainingImages[eachPlayer].append(image)
        elif self._mode == Room.Mode.ARCADE:
            max_range = min(len(self._players), 3)
            player_index = self._shuffled_players.index(player)
            for i in range(1, max_range):
                next_player = self._shuffled_players[(player_index + i) % max_range]
                self._playerToRemainingImages[next_player].append(image)

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
    
    async def beginBattle(self, bot):
        # Create a copy of the image list
        self._list_copy = self._list_of_images.copy()

        # Randomly pop two to add into the current_battle_images
        image1 = self._list_copy.pop(random.randint(0, len(self._list_copy) - 1))
        image2 = self._list_copy.pop(random.randint(0, len(self._list_copy) - 1))
        self._current_battle_images = (image1, image2)

        await self.sendBattleImages(bot)

        return

    def getBattleImages(self):
        return self._current_battle_images
    
    def getOtherBattleImage(self, image):
        if image == self._current_battle_images[0]:
            return self._current_battle_images[1]
        return self._current_battle_images[0]

    async def broadcastLeaderboardArcade(self, bot):
        # show the final leaderboard sequence
        await self.broadcast(bot, "ArcadePhase5p1", parse_mode=DialogueReader.MARKDOWN, **{'AIrtist':"a", 'captioner':"b"})
        return
    
    #Calculates the battle winner and sends the victory message to the players
    async def broadcastBattleWinner(self, bot):
        message = f"*☆☆☆☆☆Battle Results☆☆☆☆☆*\n"
        
        for image in self._current_battle_images:
            message += f"{image.showBattleVoters()}\n"

        # find the winning image by looking at the voters of both photos under battle_voters
        # handle case where there is a tie
        if self._current_battle_images[0].getVoteCount() == self._current_battle_images[1].getVoteCount():
            winner = random.choice(self._current_battle_images)
            message += f"\n*Seems like we have a tie\!*\nBut I prefer this one\!\n"
        else:
            winner = max(self._current_battle_images, key=lambda image: image.getVoteCount())

        # delete the losing image for each player (using the players messagekeys to the images, this will cause the other image to expand)
        for eachPlayer in self._players:
            await eachPlayer.deleteMessage("battle_images", itemKey=self._current_battle_images.index(winner))

            # Show who voted for which image (also show the author of the image and the caption) (Remember to store this message id in the player object)
            await eachPlayer.sendMessage(bot, message, messageKey="battle_winner", raw=True, parse_mode=DialogueReader.MARKDOWN)

        return winner
    
    async def sendBattleImages(self, bot, finals=False):
        voting_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text=f"Vote for \"{self._current_battle_images[0].getCaption()}\"", callback_data=f"{BotInitiator.BATTLE_VOTE}:0"),
                InlineKeyboardButton(text=f"Vote for \"{self._current_battle_images[1].getCaption()}\"", callback_data=f"{BotInitiator.BATTLE_VOTE}:1"),
            ]
        ])
        mediaGroup = [image.getImageURL() for image in self._current_battle_images] #TODO: Change this to the proper image canvas thing
        # delete the old leaderboard (and possibly the old media group, if editting is not possible) (player.deleteMessage should handle errors if it doesn't exist yet)
        for eachPlayer in self._players:
            await eachPlayer.deleteMessageList("battle_images")
            await eachPlayer.deleteMessage("battle_winner")

            # send the current battle images to the players (use send media group)
            await eachPlayer.sendMediaGroup(bot, mediaGroup, messageKey="battle_images") #This will set the player "battle_images" messagekey to the images

            # send the vote button again (if its the finals send a special message, send the REMATCH message if the new challenger is in the champions winstreak list)
            if finals:
                if self._current_battle_images[0].isRematch(self._current_battle_images[1]):
                    await eachPlayer.sendMessage(bot, "ArcadePhase4pRematch", messageKey="battle_winner", reply_markup=voting_keyboard)
                    continue
                await eachPlayer.sendMessage(bot, "ArcadePhase4pChallenger", messageKey="battle_winner", reply_markup=voting_keyboard)
                continue
            await eachPlayer.sendMessage(bot, "ArcadePhase4p3", messageKey="battle_winner", reply_markup=voting_keyboard) #todo set reply_markup 
        return
    
    async def advanceBattle(self, bot):
        # call broadcastBattleWinner
        winner = await self.broadcastBattleWinner(bot)
        winner.addWinstreak(self.getOtherBattleImage(winner))

        # create task that waits for 5 seconds
        wait5sec = asyncio.create_task(asyncio.sleep(5))

        # calculate the standings to find the next match, (if the list_copy is empty)
        if len(self._list_copy) > 0:
            finals = False
            # if its not the end, reset the battle_voters of the images
            for image in self._current_battle_images:
                image.resetBattleVoters()

            # reset the current_battle_images (pop the next challenger from the list_copy)
            self._current_battle_images = (winner, self._list_copy.pop(random.randint(0, len(self._list_copy) - 1)))
        else:
            # check for rematch seeing if the one with the highest winstreak is the current winner
            highestWinstreakImage = max(self._list_of_images, key=lambda image: image.getWinstreakCount())
            if highestWinstreakImage == winner:
                await wait5sec
                # broadcast the final leaderboard (broadcastLeaderboardArcade)
                await self.broadcastLeaderboardArcade(bot)
                # return True to end the room
                return True
            
            finals = True            
            self._current_battle_images = (winner, highestWinstreakImage)
        
        # finish waiting the 5 seconds
        await wait5sec

        # broadcast the next battle (sendBattleImages)
        await self.sendBattleImages(bot, finals=finals)

        return
    
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
 
                        

'''
This class will store data about a given image and its associated lies
'''

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
import random
from Player.PlayersManager import PlayersManager
import re
class Image:
    author = "a" #store author
    prompt = "a"
    correct_players = []
    imageURL = "a" #store imageURL
    imageLies = {} #store imageLies as a dict:tuple of lie_author:(lie, [list of players who fell for the lie])
    processingTime = 0 # 0 for image is made, else the number is the ETA
    requestID = 0 # 0 for image is made, else the number is the requestID

    def __init__(self, author, prompt, imageURL, processingTime = 0, requestID = 0):
        self.author = author
        self.prompt = prompt
        self.imageURL = imageURL
        self.imageLies = {}
        self.correct_players = []
        self.processingTime = processingTime
        self.requestID = requestID

    def getProcessing(self):
        return self.processingTime
    
    def getRequestID(self):
        return self.requestID

    def getImageURL(self):
        return self.imageURL
    
    def getAuthor(self):
        return self.author
    
    def getPrompt(self):
        return self.prompt

    # for each image, add a tuple for lies given by other players
    async def insertLie(self, lie, lieAuthor):
        # self.imageLies.append((lie, username, []))
        self.imageLies[lieAuthor] = (str(lie), [])

    async def addPlayersTricked(self, lieAuthor, playerTricked):
        if lieAuthor == self.author:
            # if the prompt picked was by the original author means its the truth
            self.correct_players.append(playerTricked)
            return
        self.imageLies[lieAuthor][1].append(playerTricked)
        

    def getInlineKeyboard(self, reciever):
        lie_buttons = []
        for lieAuthor, (lie, _playerTricked) in self.imageLies.items():
            if lieAuthor == reciever:
                continue
            formatted_lie = lie.replace(r":", r"\:")
            lie_button = InlineKeyboardButton(lie, callback_data=f"v:{formatted_lie}:{lieAuthor}")
            lie_buttons.append([lie_button])
        formatted_prompt = self.prompt.replace(r":", r"\:")
        prompt_button = InlineKeyboardButton(self.prompt, callback_data=f"v:{formatted_prompt}:{self.author}")
        lie_buttons.append([prompt_button])
        random.shuffle(lie_buttons)

        # add author of true prompt into dictionary
        # self.imageLies[self.author] = (self.prompt, [])

        return InlineKeyboardMarkup(lie_buttons)
    
    async def showPlayersTricked(self):
        SPECIAL_CHARACTERS = ["[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!", "*"] # [".",">","!"]        
        message = ""

        # iterate through all lies
        for lieAuthor, (lie, playersTricked) in self.imageLies.items():
            for char in SPECIAL_CHARACTERS:
                lie = lie.replace(char, f"\{char}")

            message += f"*@{lieAuthor}'s LIE: {lie}\n*"
            lieAuthorObj = PlayersManager.queryPlayer(lieAuthor)

            playersTrickedString = ", @".join(playersTricked)

            if playersTrickedString == "":
                message += "Nobody picked this lie\n"    
            else:    
                message += f"Players who picked this prompt: @{playersTrickedString}\n"
                # message += f"This was a LIE by {lieAuthor}\n"
            
            message += f"{lieAuthor} gains {len(playersTricked) * 500} points\!\n\n"
            lieAuthorObj.addScore(len(playersTricked) * 500)

        formatted_prompt = self.prompt
        for char in SPECIAL_CHARACTERS:
            formatted_prompt = formatted_prompt.replace(char, f"\{char}")

        message += f"\n*@{self.author}'s PROMPT: {formatted_prompt}\n*"
        # iterate through all players who got the right answer
        for correct_player in self.correct_players:
            message += f"Player who picked this prompt: @{correct_player}\n"
            message += f"{correct_player} gains 1000 points\!\n"
            playerObj = PlayersManager.queryPlayer(correct_player)
            playerObj.addScore(1000)

        # message += f"This was the REAL PROMPT! It was generated by {self.author}\n"
        return message
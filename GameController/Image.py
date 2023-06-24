'''
This class will store data about a given image and its associated lies
'''

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
import random
class Image:
    author = "a" #store author
    prompt = "a"
    correct_players = []
    imageURL = "a" #store imageURL
    imageLies = {} #store imageLies as a dict:tuple of lie_author:(lie, [list of players who fell for the lie])

    def __init__(self, author, prompt, imageURL):
        self.author = author
        self.prompt = prompt
        self.imageURL = imageURL
        self.imageLies = {}

    def getImageURL(self):
        return self.imageURL
    
    def getAuthor(self):
        return self.author

    # for each image, add a tuple for lies given by other players
    async def insertLie(self, lie, lieAuthor):
        # self.imageLies.append((lie, username, []))
        self.imageLies[lieAuthor] = (lie, [])

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
            lie_button = InlineKeyboardButton(lie, callback_data=f"v:{lie}:{lieAuthor}")
            lie_buttons.append([lie_button])
        prompt_button = InlineKeyboardButton(self.prompt, callback_data=f"v:{self.prompt}:{self.author}")
        lie_buttons.append([prompt_button])
        random.shuffle(lie_buttons)

        return InlineKeyboardMarkup(lie_buttons)
    
    async def showPlayersTricked(self):
        message = ""

        for lieAuthor, (lie, playersTricked) in self.imageLies.items():
            playersTrickedString = ", @".join(playersTricked)
            message += f"Prompt: {lie}\n"
            message += f"Players who picked this prompt: @{playersTrickedString}\n\n"
        
            if lieAuthor == self.author:
                message += f"This was the REAL PROMPT! It was generated by {self.author}\n"
                
                # iterate through all players who got the right answer
                for player in playersTricked:
                    message += f"{player} gains 1000 points!\n"

            else:
                message += f"This was a LIE by {lieAuthor}\n"
                message += f"{lieAuthor} gains {len(playersTricked) * 500} points!\n"

        return message
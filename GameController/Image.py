'''
This class will store data about a given image and its associated lies
'''

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
import random
class Image:
    author = "a" #store author
    prompt = "a"
    imageURL = "a" #store imageURL
    imageLies = {} #store imageLies as a dict:tuple of lie_author:(lie, [list of players who fell for the lie])

    def __init__(self, author, prompt, imageURL):
        self.author = author
        self.prompt = prompt
        self.imageURL = imageURL
        self.imageLies = []

    def getImageURL(self):
        return self.imageURL
    
    def getAuthor(self):
        return self.author

    # for each image, add a tuple for lies given by other players
    async def insertLie(self, lie, username):
        # self.imageLies.append((lie, username, []))
        self.imageLies[username] = (lie, [])

    async def addPlayersTricked(self, author, player):
        self.imageLies[author][1].append(player.getUsername())

    def getInlineKeyboard(self):
        lie_buttons = []
        for lie, currPlayerUsername in self.imageLies:
            lie_button = InlineKeyboardButton(lie, callback_data=f"vote:{currPlayerUsername}")
            lie_buttons.append([lie_button])
        prompt_button = InlineKeyboardButton(self.prompt, callback_data=f"vote:{self.author}")
        lie_buttons.append([prompt_button])
        random.shuffle(lie_buttons)

        return InlineKeyboardMarkup(lie_buttons)


    
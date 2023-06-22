'''
This class will store data about a given image and its associated lies
'''

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
import random
class Image:
    author = "a" #store author
    prompt = "a"
    imageURL = "a" #store imageURL
    imageLies = [] #store imageLies as a tuple of (lie, player)

    def __init__(self, author, prompt, imageURL):
        self.author = author
        self.prompt = prompt
        self.imageURL = imageURL
        self.imageLies = []

    def getImageURL(self):
        return self.imageURL

    # for each image, add a tuple for lies given by other players
    async def insertLie(self, lie, username):
        self.imageLies.append((lie, username))

    def getInlineKeyboard(self):
        lie_buttons = []
        for lie, currPlayer in self.imageLies:
            lie_button = InlineKeyboardButton(lie, callback_data=f"vote:{self.imageURL}:{currPlayer}")
            lie_buttons.append([lie_button])
        prompt_button = InlineKeyboardButton(self.prompt, callback_data=f"vote:{self.imageURL}:{self.author}")
        lie_buttons.append([prompt_button])
        random.shuffle(lie_buttons)

        return InlineKeyboardMarkup(lie_buttons)


    
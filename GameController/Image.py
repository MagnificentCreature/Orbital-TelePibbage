'''
This class will store data about a given image and its associated lies
'''

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
import random
from Player.PlayersManager import PlayersManager
from BotController import BotInitiator
import re
import urllib.request
import PIL.Image as MyImage
from PIL import ImageFont, ImageDraw
import textwrap

IMAGE_ASSETS_PATH = "Assets\\Images\\"
FONT_ASSETS_PATH = "Assets\\Font\\"
class Image:
    author = "" #store author
    prompt = ""
    correct_players = []
    imageURL = "" #store imageURL
    imageCaptions = [] #store imageCaptions as a list of tuples: (caption, username)
    choosenCaption = ("", "") #store the choosen caption as a tuple: (caption, caption_author)
    imageLies = {} #store imageLies as a dict:tuple of lie_author:(lie, [list of players who fell for the lie])
    processingTime = 0 # 0 for image is made, else the number is the ETA
    requestID = 0 # 0 for image is made, else the number is the requestID
    battle_voters = [] # store the voters for the battle
    winstreak = [] #Winstreak for the gaunlet stored as a list of defeated images

    def __init__(self, author, prompt, imageURL, processingTime = 0, requestID = 0):
        self.author = author
        self.prompt = prompt
        self.imageURL = imageURL
        self.imageLies = {}
        self.correct_players = []
        self.processingTime = processingTime
        self.requestID = requestID
        self.imageCaptions = []
        self.choosenCaption = ()
        self.battle_voters = []
        self.winstreak = []

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

    async def insertCaption(self, caption, captionAuthor):
        self.imageCaptions.append((caption, captionAuthor))

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
            lie_button = InlineKeyboardButton(lie, callback_data=f"{BotInitiator.VOTE}:{lieAuthor}")
            lie_buttons.append([lie_button])
        prompt_button = InlineKeyboardButton(self.prompt, callback_data=f"{BotInitiator.VOTE}:{self.author}")
        lie_buttons.append([prompt_button])
        random.shuffle(lie_buttons)

        # add author of true prompt into dictionary
        # self.imageLies[self.author] = (self.prompt, [])

        return InlineKeyboardMarkup(lie_buttons)
    
    def getCaptionKeyboard(self):
        caption_buttons = []
        for i, (caption, _author) in enumerate(self.imageCaptions):
            caption_button = InlineKeyboardButton(caption, callback_data=f"{BotInitiator.CAPTION}:{i}:{_author}")
            caption_buttons.append([caption_button])
        # random.shuffle(caption_buttons)
        return InlineKeyboardMarkup(caption_buttons)
    
    def selectCaption(self, captionNum, author):
        self.choosenCaption = (self.imageCaptions[captionNum][0], author)

    def getCaption(self):
        return self.choosenCaption[0]
    
    def getCaptionAuthor(self):
        return self.choosenCaption[1]
    
    def addBattleVoter(self, voter):
        self.battle_voters.append(voter)

    def getVoteCount(self):
        return len(self.battle_voters)
    
    def addWinstreak(self, image):
        self.winstreak.append(image)

    def resetBattleVoters(self):
        self.battle_voters = []

    def showBattleVoters(self):
        message = ""
        message += f"Votes for {self.author}'s image and {self.choosenCaption[1]} caption:\n"
        for voter in self.battle_voters:
            message += f"@{voter}\n"
        return message
    
    def getWinstreakCount(self):
        return len(self.winstreak)

    def isRematch(self, otherImage):
        return otherImage in self.winstreak
    
    async def showPlayersTricked(self):
        SPECIAL_CHARACTERS = ["[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!", "*"] # [".",">","!"]        
        message = ""

        # iterate through all lies
        for lieAuthor, (lie, playersTricked) in self.imageLies.items():
            for char in SPECIAL_CHARACTERS:
                lie = lie.replace(char, f"\{char}")

            message += f"\*@{lieAuthor}'s LIE: {lie}\*\n"
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

        message += f"\n\*@{self.author}'s PROMPT: {formatted_prompt}\*\n"
        # iterate through all players who got the right answer
        for correct_player in self.correct_players:
            message += f"Player who picked this prompt: @{correct_player}\n"
            message += f"{correct_player} gains 1000 points\!\n"
            playerObj = PlayersManager.queryPlayer(correct_player)
            playerObj.addScore(1000)

        # message += f"This was the REAL PROMPT! It was generated by {self.author}\n"
        return message
    
    async def showBestPrompt(self):

        # obtain text
        sortedLies = sorted(self.imageLies.items(), key=lambda x:len(x[1][1]), reverse=True)
        mostPopularPrompt = sortedLies[0][1][0]

        print(mostPopularPrompt)

        # obtain photo frame
        urllib.request.urlretrieve("https://i.imgur.com/UN0tpJR.png", f"{IMAGE_ASSETS_PATH}bgFrame.png")
        # urllib.request.urlretrieve("https://i.imgur.com/EdSQzFR.png", "sample.png")
        # remove "\" from self.imageURL"
        self.newImageURL = re.sub(r"\\", "", self.imageURL)
        print("new image url: "self.newImageURL)
        urllib.request.urlretrieve(self.newImageURL, "sample.png")
        sample = MyImage.open("sample.png")
        # urllib.request.urlretrieve(self.imageURL, "sample.png")
        background = MyImage.open(f"{IMAGE_ASSETS_PATH}bgFrame.png")
        # sample = MyImage.open("sample.png")

        background.paste(sample, (245, 206))

        # text = "hello WORLD how are you doing my friend, this is aNEWWWWWWW ERAA, sdgugew fugwefw wewefuwefiwefw ewfuwefuigwegf"
        lines = textwrap.wrap(mostPopularPrompt, width=40, max_lines=2)

        # Starting position of the text in canvas
        x = 105  
        y = 840 
        #hardcode height
        y_text =  40

        font = ImageFont.truetype(f"{FONT_ASSETS_PATH}GrenzeGotisch-Regular.ttf", 50)

        # Create a text image with the text placed within the box
        text_draw = ImageDraw.Draw(background)

        for line in lines:
            print('h')
            line_width = font.getlength(line)
            text_draw.text((x, y), line, font=font, fill=(0, 0, 0))
            y += y_text

        # Save the final image
        background.save("finalImg.png")
        
        print('got to end')
        # with open('finalImg.png', 'rb') as img:
        #     await context.bot.send_photo(chat_id=update.message.from_user.id, photo=img)
'''
This class will store data about a given image and its associated lies
'''

import os
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import random
from BotController.BotInitiatorConstants import BotInitiatorConstants
from Chat.DialogueReader import DialogueReader
from Player.PlayersManager import PlayersManager
import urllib.request
import requests
from io import BytesIO
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
    framedImage = None
    captionedImage = None

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
        self.framedImage = None
        self.captionedImage = None


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
            lie_button = InlineKeyboardButton(lie, callback_data=f"{BotInitiatorConstants.VOTE}:{lieAuthor}")
            lie_buttons.append([lie_button])
        prompt_button = InlineKeyboardButton(self.prompt, callback_data=f"{BotInitiatorConstants.VOTE}:{self.author}")
        lie_buttons.append([prompt_button])
        random.shuffle(lie_buttons)

        # add author of true prompt into dictionary
        # self.imageLies[self.author] = (self.prompt, [])

        return InlineKeyboardMarkup(lie_buttons)
    
    def getCaptionKeyboard(self):
        caption_buttons = []
        for i, (caption, _author) in enumerate(self.imageCaptions):
            caption_button = InlineKeyboardButton(caption, callback_data=f"{BotInitiatorConstants.CAPTION}:{i}:{_author}")
            caption_buttons.append([caption_button])
        # random.shuffle(caption_buttons)
        return InlineKeyboardMarkup(caption_buttons)
    
    def selectCaption(self, captionNum, author):
        self.choosenCaption = (self.imageCaptions[captionNum][0], author)
        self.captionImage()

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
        formattedAuthor = self.author.replace("_", "\_")
        formattedCaptionAuthor = self.getCaptionAuthor().replace("_", "\_")
        message += f"Votes for {formattedAuthor}'s image with {formattedCaptionAuthor} caption:\n"
        for voter in self.battle_voters:
            voter = voter.replace("_", "\_")
            message += f"@{voter}\n"
        return message
    
    def getWinstreakCount(self):
        return len(self.winstreak)

    def isRematch(self, otherImage):
        return otherImage in self.winstreak
    
    async def showPlayersTricked(self):
        message = ""

        # iterate through all lies
        for lieAuthor, (lie, playersTricked) in self.imageLies.items():

            formattedLieAuthor = lieAuthor.replace("_", "\_")
            message += f"*@{formattedLieAuthor}'s LIE: {lie}*\n"
            # message += f"@{lieAuthor}'s LIE: {lie}\n"
            
            lieAuthorObj = PlayersManager.queryPlayer(lieAuthor)

            playersTrickedFormatted = [name.replace('_', '\_') for name in playersTricked]
            playersTrickedString = ", @".join(playersTrickedFormatted)

            if playersTrickedString == "":
                message += "Nobody picked this lie\n"    
            else:    
                message += f"Players who picked this prompt: @{playersTrickedString}\n"
                # message += f"This was a LIE by {lieAuthor}\n"
            
            message += f"{formattedLieAuthor} gains {len(playersTricked) * 500} points\!\n\n"
            # message += f"{formattedLieAuthor} gains {len(playersTricked) * 500} points!\n\n"
            lieAuthorObj.addScore(len(playersTricked) * 500)

        formatted_prompt = DialogueReader.parseFormatting(self.prompt)

        message += f"\n*@{self.author}'s REAL PROMPT: {formatted_prompt}*\n"
        # message += f"\n*@{self.author}'s PROMPT: {formatted_prompt}*\n"
        # iterate through all players who got the right answer
        for correct_player in self.correct_players:
            formattedCorrectPlayer = correct_player.replace("_", "\_")
            message += f"Player who picked this prompt: @{formattedCorrectPlayer}\n"
            message += f"{correct_player} gains 1000 points\!\n"
            # message += f"{formattedCorrectPlayer} gains 1000 points!\n"
            playerObj = PlayersManager.queryPlayer(correct_player)
            playerObj.addScore(1000)

        # message += f"This was the REAL PROMPT! It was generated by {self.author}\n"
        return message
    
    def saveFrameImage(self, custom_caption=None):
        # add original prompt to dictionary of image lies
        # self.imageLies[self.author] = (self.prompt, self.correct_players)
        # obtain text
        if custom_caption is None:
            sortedLies = sorted(self.imageLies.items(), key=lambda x:len(x[1][1]), reverse=True)
            mostPopularPrompt = f"PIBBAGE! {sortedLies[0][1][0]}"
            # sum every vote count
            totalVotes = 0
            for _, (_, playersTricked) in self.imageLies.items():
                totalVotes += len(playersTricked)
            totalVotes += len(self.correct_players)

            if len(sortedLies[0][1][1])/totalVotes < 0.8:
                return False
        else:
            mostPopularPrompt = custom_caption
        # del self.imageLies[self.author] # remove original prompt from dictionary of image lies

        # When reacing this point, it means the lie is popular, so save it as a framed image.

        # check if there is already a bgFrame.png
        if not os.path.isfile(f"{IMAGE_ASSETS_PATH}bgFrame.png"):
            urllib.request.urlretrieve("https://i.imgur.com/UN0tpJR.png", f"{IMAGE_ASSETS_PATH}bgFrame.png")
        background = MyImage.open(f"{IMAGE_ASSETS_PATH}bgFrame.png")

        response = requests.get(self.imageURL)    
        response.raise_for_status()
        sample = MyImage.open(BytesIO(response.content))

        background.paste(sample, (245, 206))

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
            text_draw.text((x, y), line, font=font, fill=(0, 0, 0))
            y += y_text

        self.framedImage = background
        return True
    
    def getFramedImage(self):
        bio = BytesIO() # got to import BytesIO from io
        framedFinalImage = self.framedImage
        framedFinalImage.save(bio, 'PNG')
        bio.seek(0)

        return bio

    def captionImage(self):

        caption = self.choosenCaption[0]

        response = requests.get(self.imageURL)    
        response.raise_for_status()

        imagePng = MyImage.open(BytesIO(response.content))
        
        font = ImageFont.truetype(f"{FONT_ASSETS_PATH}arial.ttf", 30)
        # calc position of text
        draw = ImageDraw.Draw(imagePng)

        left, top, right, bottom = draw.textbbox((0,0), caption, font=font)
        text_width = right - left
        text_height = top - bottom

        y_text = 40

        lines = textwrap.wrap(caption, width=27, max_lines=3)

        for i, line in enumerate(lines):
            left, top, right, bottom = draw.textbbox((0,0), line, font=font)
            text_width = right - left
            text_height = top - bottom
            x = (imagePng.width - text_width) // 2
            y = (imagePng.height - text_height) // 2 + 100
            draw.text((x, y + i*y_text), line, font=font, fill="black", stroke_width=2, stroke_fill="white")

        self.captionedImage = imagePng

    def getCaptionedImage(self):
        bio = BytesIO() # got to import BytesIO from io
        captionedFinalImage = self.captionedImage
        captionedFinalImage.save(bio, 'PNG')
        bio.seek(0)

        return bio

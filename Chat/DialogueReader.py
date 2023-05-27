"""
This class reads dialogues from dialogues.txt and stores them in a dictionary
This class is responsible for sending chat messages
Calls to this class can be made from the public function sendMessage(bot, chat, message)
"""

from os import path
from Player.PlayersManager import PlayersManager
# from telegram import Bot, Update

class DialogueReader:

    # Create a static variable to store the dialogues
    dialogues = {}

    def readDialogues(filepath):
        with open(filepath, 'r') as f: 
            # Read the contents of the file into a list 
            lines = f.readlines() 
            # Create an empty dictionary 
            data = {} 
            # Loop through the list of lines 
            for line in lines: 
                if (line[0] == "#"):
                    continue
                # Split the line into key-value pairs by the first comma
                key, value = line.strip().split(',', 1)
                # Store the key-value pairs in the dictionary 
                data[key] = value
            # Return the dictionary
            return data

    dir_path = path.dirname(path.realpath(__file__))
    dialogues_path = path.join(dir_path, "Dialogues.txt")

    # Read the dialogues from the file

    dialogues = readDialogues(dialogues_path)

    def additionalProcessing(inputString):
        # Replace \n with newline
        inputString = inputString.replace("\\n", "\n")
        return inputString
    
    @staticmethod
    def getMesssage(key):
        return DialogueReader.additionalProcessing(DialogueReader.dialogues[key])

    @staticmethod
    async def sendMessageByID(bot, chat_id, message):
        #Use telegram api to send a message
        if (message not in DialogueReader.dialogues):
            print("Message " + message + " not found in dialogues.txt")
        formattedText = DialogueReader.additionalProcessing(DialogueReader.dialogues[message])
        await bot.send_message(chat_id=chat_id, text=formattedText)

    @staticmethod
    async def sendMessageByID(bot, chat_id, message, **kwargs):
        #Use telegram api to send a message, additional arguments are given in the form of **{{key}=value}
        if (message not in DialogueReader.dialogues):
            print("Message " + message + " not found in dialogues.txt")
        formattedText = DialogueReader.additionalProcessing(DialogueReader.dialogues[message].format(**kwargs))
        await bot.send_message(chat_id=chat_id, text=formattedText)
    
    @staticmethod
    async def sendImageURLByID(bot, chat_id, imageURL):
        await bot.send_photo(chat_id=chat_id, photo=imageURL)
        
    @staticmethod
    async def sendMessage(bot, username, message):
        #Use telegram api to send a message
        if (message not in DialogueReader.dialogues):
            print("Message " + message + " not found in dialogues.txt")
        formattedText = DialogueReader.additionalProcessing(DialogueReader.dialogues[message])
        await bot.send_message(chat_id=PlayersManager.getChatID(username), text=formattedText)

    @staticmethod
    async def sendMessage(bot, username, message, **kwargs):
        #Use telegram api to send a message, additional arguments are given in the form of **{{key}=value}
        if (message not in DialogueReader.dialogues):
            print("Message " + message + " not found in dialogues.txt")
        formattedText = DialogueReader.additionalProcessing(DialogueReader.dialogues[message].format(**kwargs))
        await bot.send_message(chat_id=PlayersManager.getChatID(username), text=formattedText)

    @staticmethod
    async def sendImageURL(bot, username, imageURL):
        await bot.send_photo(chat_id=PlayersManager.getChatID(username), photo_url=imageURL)

    # def readDialogues(filepath):
    #     with open(filepath, 'r') as f: 
    #         # Read the contents of the file into a list 
    #         lines = f.readlines() 
    #         # Create an empty dictionary 
    #         data = {} 
    #         # Loop through the list of lines 
    #         for line in lines: 
    #             # Split the line into key-value pairs 
    #             key, value = line.strip().split(',') 
    #             # Store the key-value pairs in the dictionary 
    #             data[key] = value 
    #         # Return the dictionary
    #         return data
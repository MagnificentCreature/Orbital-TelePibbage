"""
This class reads _dialogues from _dialogues.txt and stores them in a dictionary
This class is responsible for sending chat messages
Calls to this class can be made from the public function sendMessage(bot, chat, message)
"""

from os import path
from BotController import BotInitiator
import logging

from telegram import error

class DialogueReader:

    # Create a static variable to store the dialogues
    _dialogues = {}

    def __read_dialogues(filepath):
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

    _dir_path = path.dirname(path.realpath(__file__))
    _dialogues_path = path.join(_dir_path, "dialogues.txt")

    # Read the dialogues from the file

    _dialogues = __read_dialogues(_dialogues_path)

    @staticmethod
    def additionalProcessing(inputString):
        # Replace \n with newline
        inputString = inputString.replace("\\n", "\n")
        return inputString
    
    @classmethod
    def queryDialogue(cls, key):
        return cls.additionalProcessing(cls._dialogues[key])
    
    @classmethod
    def queryDialogue(cls, key, **kwargs):
        return cls.additionalProcessing(cls._dialogues[key].format(**kwargs))

    @classmethod
    async def sendMessageByID(cls, bot, chat_id, message, reply_markup=None):
        #Use telegram api to send a message
        if (message not in cls._dialogues):
            print("Message " + message + " not found in dialogues.txt")
        formattedText = cls.additionalProcessing(cls._dialogues[message])
        try:
            return await bot.send_message(chat_id=chat_id, text=formattedText, reply_markup=reply_markup)
        except error.Forbidden as e:
            logging.error("Error sending message to chat_id " + str(chat_id) + ": " + str(e))

    @classmethod
    async def sendMessageByID(cls, bot, chat_id, message, reply_markup=None, **kwargs):
        #Use telegram api to send a message, additional arguments are given in the form of **{{key}=value}
        if (message not in cls._dialogues):
            print("Message " + message + " not found in dialogues.txt")
        formattedText = cls.additionalProcessing(cls._dialogues[message].format(**kwargs))
        try:
            return await bot.send_message(chat_id=chat_id, text=formattedText, reply_markup=reply_markup)
        except error.Forbidden as e:
            logging.error("Error sending message to chat_id " + str(chat_id) + ": " + str(e))
    
    @staticmethod
    async def sendImageURLByID(bot, chat_id, imageURL, reply_markup=None):
        try:
            return await bot.send_photo(chat_id=chat_id, photo=imageURL, reply_markup=reply_markup)
        except error.Forbidden as e:
            logging.error("Error sending message to chat_id " + str(chat_id) + ": " + str(e))
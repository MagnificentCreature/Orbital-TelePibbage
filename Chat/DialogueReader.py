"""
This class reads _dialogues from _dialogues.txt and stores them in a dictionary
This class is responsible for sending chat messages
Calls to this class can be made from the public function sendMessage(bot, chat, message)
"""

import asyncio
from os import path
import random
from BotController import BotInitiator
import logging

from telegram import error
from telegram import constants


class DialogueReader:

    MAX_RETRIES = 5
    # Constant for 
    MARKDOWN = constants.ParseMode.MARKDOWN_V2
    
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
        SPECIAL_CHARACTERS = ["[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"] # [".",">","!"]
        # Replace new line characters with \n
        inputString = inputString.replace("\\n", "\n")
        # Replace special characters with \<character> for telegram compliance
        for eachItem in SPECIAL_CHARACTERS:
            inputString = inputString.replace(eachItem, f"\{eachItem}")
        # capitalise the first letter
        inputString = inputString[0].upper() + inputString[1:]
        return inputString
    
    @classmethod
    def queryDialogue(cls, key):
        return cls.additionalProcessing(cls._dialogues[key])
    
    @classmethod
    def queryDialogue(cls, key, **kwargs):
        return cls.additionalProcessing(cls._dialogues[key].format(**kwargs))

    @classmethod
    async def sendMessageByID(cls, bot, chat_id, message, reply_markup=None, raw=False, exponential_backoff=1, parse_mode=MARKDOWN):
        try:
            #Use telegram api to send a message
            try:
                if raw:
                    return await bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup, parse_mode=parse_mode) 
                if (message not in cls._dialogues):
                    print("Message " + message + " not found in dialogues.txt")
                formattedText = cls.additionalProcessing(cls._dialogues[message])
                return await bot.send_message(chat_id=chat_id, text=formattedText, reply_markup=reply_markup, parse_mode=parse_mode)
            except error.Forbidden as e:
                logging.error("Error sending message to chat_id " + str(chat_id) + ": " + str(e))
        except error.TimedOut as e:
            if exponential_backoff > cls.MAX_RETRIES:
                print("FAILURE TO SEND, ABORTING")
                return
            logging.error("Timeout error sending message to chat_id " + str(chat_id) + ": " + str(e))
            asyncio.sleep(2**random.randint(1, exponential_backoff))
            return await cls.sendMessageByID(bot, chat_id, message, reply_markup=reply_markup, raw=raw, exponential_backoff=exponential_backoff+1, parse_mode=parse_mode)


    @classmethod
    async def sendMessageByID(cls, bot, chat_id, message, reply_markup=None, raw=False, exponential_backoff=1, parse_mode=MARKDOWN, **kwargs):
        try:
            #Use telegram api to send a message, additional arguments are given in the form of **{{key}=value}
            try:
                if raw:
                    return await bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup, parse_mode=parse_mode)
                if (message not in cls._dialogues):
                    print("Message " + message + " not found in dialogues.txt")
                formattedText = cls.additionalProcessing(cls._dialogues[message].format(**kwargs))
                return await bot.send_message(chat_id=chat_id, text=formattedText, reply_markup=reply_markup, parse_mode=parse_mode)
            except error.Forbidden as e:
                logging.error("Error sending message to chat_id " + str(chat_id) + ": " + str(e))
        except error.TimedOut as e:
            if exponential_backoff > cls.MAX_RETRIES:
                print("FAILURE TO SEND, ABORTING")
                return
            logging.error("Timeout error sending message to chat_id " + str(chat_id) + ": " + str(e))
            logging.info("Retrying with exponential backoff of " + str(2**exponential_backoff) + " seconds")
            await asyncio.sleep(2**random.randint(1, exponential_backoff))
            return await cls.sendMessageByID(bot, chat_id, message, reply_markup=reply_markup, raw=raw, exponential_backoff=exponential_backoff+1, parse_mode=parse_mode, **kwargs)
    
    @classmethod
    async def sendImageURLByID(cls, bot, chat_id, imageURL, caption=None, exponential_backoff=1, reply_markup=None, parse_mode=MARKDOWN):
        try:
            try:
                return await bot.send_photo(chat_id=chat_id, photo=imageURL, reply_markup=reply_markup, caption=caption, parse_mode=parse_mode)
            except error.Forbidden as e:
                logging.error("Error sending message to chat_id " + str(chat_id) + ": " + str(e))
        except error.TimedOut as e:
            if exponential_backoff > cls.MAX_RETRIES:
                print("FAILURE TO SEND, ABORTING")
                return
            logging.error("Timeout error sending message to chat_id " + str(chat_id) + ": " + str(e))
            logging.info("Retrying with exponential backoff of " + str(2**exponential_backoff) + " seconds")
            asyncio.sleep(2**random.randint(1, exponential_backoff))
            return await cls.sendImageURLByID(bot, chat_id, imageURL, reply_markup=reply_markup, exponential_backoff=exponential_backoff+1, parse_mode=parse_mode)

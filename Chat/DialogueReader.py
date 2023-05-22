"""
This class reads dialogues from dialogues.txt and stores them in a dictionary
This class is responsible for sending chat messages
Calls to this class can be made from the public function sendMessage(bot, chat, message)
"""

from os import path
# from telegram import Bot, Update

class DialogueReader:

    # Create a static variable to store the dialogues
    dialogues = {}

    file_path = path.realpath(__file__)
    dir_path = path.dirname(file_path)
    dialogues_path = path.join(dir_path, "Dialogues.txt")

    # Read the dialogues from the file
    with open(dialogues_path, 'r') as f: 
        # Read the contents of the file into a list 
        lines = f.readlines() 
        # Create an empty dictionary 
        data = {} 
        # Loop through the list of lines 
        for line in lines: 
            # Split the line into key-value pairs by the first comma
            key, value = line.strip().split(',', 1)
            # Store the key-value pairs in the dictionary 
            data[key] = value
        dialogues = data
    
    @staticmethod
    def additionalProcessing(inputString):
        # Replace \n with newline
        inputString = inputString.replace("\\n", "\n")
        return inputString

    @staticmethod
    async def sendMessage(bot, update, message):
        #Use telegram api to send a message
        if (message not in DialogueReader.dialogues):
            print("Message " + message + " not found in dialogues.txt")
        formattedText = DialogueReader.additionalProcessing(DialogueReader.dialogues[message])
        await bot.send_message(chat_id=update.effective_chat.id, text=formattedText)
        
    @staticmethod
    async def sendMessage(bot, update, message, **kwargs):
        #Use telegram api to send a message
        if (message not in DialogueReader.dialogues):
            print("Message " + message + " not found in dialogues.txt")
        formattedText = DialogueReader.additionalProcessing(DialogueReader.dialogues[message].format(**kwargs))
        await bot.send_message(chat_id=update.effective_chat.id, text=formattedText)

    

    # def readDialogues():
    #     with open('Dialogues.txt', 'r') as f: 
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
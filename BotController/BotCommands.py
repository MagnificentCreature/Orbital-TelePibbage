"""
Handles user commands
"""

import asyncio
import time

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from BotController import BotCommands
from telegram.ext import (
    # Application,
    CallbackQueryHandler,
    # CommandHandler,
    ContextTypes,
    # ConversationHandler,
    # MessageHandler,
    # filters,
)

import sys
from pathlib import Path

from Player.Player import Player
sys.path.insert(1, str(Path(__file__).parent.parent.absolute()))
from Chat.DialogueReader import DialogueReader
from Room.RoomHandler import RoomHandler
from Player.PlayersManager import PlayersManager
from ImageGeneration import ImageGenerator
from BotController import BotInitiator

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await PlayersManager.recordNewPlayer(update.message.from_user.username, update.message.from_user.id, context.user_data)
    await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "Welcome1")
    
    if (context.args):
        roomCode = context.args[0]        
        return await join_room(update, context, roomCode)
    
    await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "Welcome2", reply_markup=BotInitiator.WelcomeKeyboard)
    return BotInitiator.FRESH

async def create_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await DialogueReader.sendMessageByID(context.bot, update.callback_query.from_user.id, "CreateRoom1")
    await RoomHandler.generateRoom(update.callback_query.from_user.username, context.bot)
    return BotInitiator.INROOM

async def join_room_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(text=DialogueReader.queryDialogue("EnterCode"), reply_markup=BotInitiator.ReenterKeyboard)
    return BotInitiator.ENTERCODE

async def join_room_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    room_code = update.message.text
    return await join_room(update, context, room_code)

async def join_room(update: Update, context: ContextTypes.DEFAULT_TYPE, roomCode=None):
    # Technically this part of the code is no longer necessary, this is only if the user does
    # /join_room <room_code> as a command, now all calls to join_room have a roomCode in it
    try:
        if roomCode is None:
            roomCode = update.message.text.split(" ")[1]
    except IndexError:
        await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "InvalidRoom")
        return BotInitiator.FRESH
    
    await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "JoinRoom1", **{"roomCode": roomCode})
    success = await RoomHandler.joinRoom(update.message.from_user.username, roomCode, context.bot)
    
    if not success:
        await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "InvalidRoom")
        await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "ReenterCode", reply_markup=BotInitiator.ReenterKeyboard)
        return BotInitiator.ENTERCODE

    # waiting_to_start = asyncio.Event()
    # context.user_data["waiting_to_start"] = waiting_to_start
    # await waiting_to_start.wait()
    # del context.user_data['waiting_to_start']

    # if context.user_data['roomCode'] == "": # If the user left the room, send a new welcome message
    #     await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "Welcome2", reply_markup=BotInitiator.WelcomeKeyboard)
    #     return BotInitiator.FRESH
    
    return BotInitiator.INROOM

async def return_to_fresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data['roomCode'] == "":
        await update.callback_query.edit_message_text(text=DialogueReader.queryDialogue("ReturningToStart"))
    else:
        await update.callback_query.delete_message()
        await RoomHandler.leaveRoom(update.callback_query.from_user.username, context.bot)
    await DialogueReader.sendMessageByID(context.bot, update.callback_query.from_user.id, "Welcome2", reply_markup=BotInitiator.WelcomeKeyboard)
    return BotInitiator.FRESH

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = (" ").join(update.message.text.split(" ")[1:]) #TODO logic flow if invalid prompt or no prompt
    imageurl = await ImageGenerator.imageQuery(prompt) 
    print(update.message.from_user.username + "Generated Image: " + str(imageurl))
    await DialogueReader.sendImageURLByID(context.bot, update.message.from_user.id, imageurl)

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await RoomHandler.startGame(update.callback_query.from_user.username, context.bot)
    return BotInitiator.PROMPTING_PHASE

async def take_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Check if the user is in a game
    if not context.user_data['in_game']:
        return BotInitiator.WAITING_FOR_HOST
    # TODO: handle bad prompts or failure to generate image
    #asyncio.wait_for(ImageGenerator.imageQuery(update.message).wait(), timeout=60)

    message_text = update.message.text
    # print('image generated')
    await context.bot.send_message(chat_id=update.effective_chat.id, text='image generated')
    #to save api tokens, uncomment when ready
    # imageurl = await ImageGenerator.imageQuery(update.message.text) 
    # PlayersManager.setImageURL(update.message.from_user.username, imageURL=str(imageurl))
    # #RoomHandler.test(update.message.from_user.username)
    # await DialogueReader.sendImageURLByID(context.bot, update.message.from_user.id, imageurl)

    #context.user_data['phase'] = Player.PROMPTING_PHASE
    #message is sent, so move to next phase alr
    PlayersManager.setPromptSent(update.message.from_user.username)
    # context.user_data['phase'] = Player.LYING_PHASE

    # booly = False
    # while not booly:
    #     print('not yet')
    #     await asyncio.sleep(5)
    #     booly = await RoomHandler.allSentPrompts(update.message.from_user.username)

    booly = await RoomHandler.allSentPrompts(update.message.from_user.username)
    if booly:
        RoomHandler.setAllUserDataPhase(update.message.from_user.username, Player.LYING_PHASE)
    # await wait_for_all_players(update, context)
    # print('alls gd')

    return BotInitiator.LYING_PHASE

async def phaseTest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('initiate test')
    message_text = update.message.text
    # print('image generated')
    # if player in lying phase, means all players in lying phase
    if context.user_data['phase'] == Player.LYING_PHASE:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='everyone in')
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='not everyone in')
# async def wait_for_all_players(update, context: ContextTypes.DEFAULT_TYPE):
#     room_code = context.user_data['roomCode']
#     room = RoomHandler.getRoom(room_code)

#     booly = False

#     # while not booly:
#     #     print('not yet')
#     #     booly = await room.allSentPrompts()
#     #     await asyncio.sleep(3)

#     while not room.allSentPrompts():
#         print('not yet')
#         await asyncio.sleep(3)
        
# # while not room.allSentPrompts():
# # await asyncio.sleep(1)
# async def process_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
#     thisPlayer = PlayersManager.queryPlayer(update.message.from_user.username)
#     roomCode = thisPlayer.getRoomCode()
#     players = RoomHandler.returnPlayers(roomCode)
#     print(players)
#     tasks = []

#     if players is not None:
#         for player in players:
#             if player is not None:
#                 await take_prompt(update, context)  # Call take_prompt for each player individually
#     # for player in players:
#     #     if player is not None:  # Check if player is not None
#     #         task = asyncio.create_task(take_prompt(update, context))
#     #         tasks.append(task)

#     # await asyncio.gather(*tasks)

# # async def handle_player_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
# #     task = asyncio.create_task(take_prompt(update, context))
# #     # You can store the task object and use it later if needed

# #     # Continue with other processing or await the task to complete
# #     await task

async def take_lie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Check if the user is in a game
    if not context.user_data['in_game']:
        return BotInitiator.WAITING_FOR_HOST
    
    # check if the user is in the lying phase
    if context.user_data['phase'] != Player.LYING_PHASE:
        # TODO Handle the phase error
        return BotInitiator.PROMPTING_PHASE
    
    # TODO handle lies and continue the gameplay

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "UnknownCommand")
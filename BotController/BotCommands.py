"""
Handles user commands
"""

import asyncio

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

game_started_event = asyncio.Event()

import sys
from pathlib import Path
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
    print("Returning to fresh")
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
        return BotInitiator.INROOM
    # TODO: if not handle prompt
    return BotInitiator.SENT_PROMPT

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "UnknownCommand")
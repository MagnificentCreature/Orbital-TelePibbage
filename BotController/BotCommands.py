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
    await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "Welcome2", reply_markup=BotInitiator.WelcomeKeyboard)
    
    if (context.args):
        roomCode = context.args[0]
        await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "JoinRoom1", **{"roomCode": roomCode})
        await RoomHandler.joinRoom(update.message.from_user.username, roomCode, context.bot)

        return BotInitiator.INROOM
    
    return BotInitiator.FRESH

async def create_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "CreateRoom1")
    #await RoomHandler.generateRoom(update.message.from_user.username, context.bot)
    await DialogueReader.sendMessageByID(context.bot, update.callback_query.from_user.id, "CreateRoom1")
    await RoomHandler.generateRoom(update.callback_query.from_user.username, context.bot)

    await DialogueReader.sendMessageByID(context.bot, update.callback_query.from_user.id, "StartGameOption", reply_markup=BotInitiator.StartGameKeyboard)

    return BotInitiator.INROOM

# async def join_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     try:
#         roomCode = update.message.text.split(" ")[1]
#     except IndexError:
#         await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "RoomNotFound")
#         return
    
#     await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "JoinRoom1", **{"roomCode": roomCode})
#     await RoomHandler.joinRoom(update.message.from_user.username, roomCode, context.bot)

#     return BotInitiator.INROOM

async def join_room_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return BotInitiator.ENTERCODE

async def join_room_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    room_code = update.message.text

    await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "JoinRoom1", **{"roomCode": room_code})
    await RoomHandler.joinRoom(update.message.from_user.username, room_code, context.bot)

    #player skips inRoom

    #testing
    await game_started_event.wait()
    
    await DialogueReader.sendMessageByID(context.bot, update.callback_query.from_user.id, "CreateRoom1")

    return BotInitiator.INGAME

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = (" ").join(update.message.text.split(" ")[1:]) #TODO logic flow if invalid prompt or no prompt
    imageurl = await ImageGenerator.imageQuery(prompt)
    print(update.message.from_user.username + "Generated Image: " + str(imageurl))
    await DialogueReader.sendImageURLByID(context.bot, update.message.from_user.id, imageurl)

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await DialogueReader.sendMessageByID(context.bot, update.callback_query.from_user.id, "StartGameWelcome")
    #await PromptHandler.start_phase1(update, context)

    #testing
    game_started_event.set()

    await DialogueReader.sendMessageByID(context.bot, update.callback_query.from_user.id, "CreateRoom1")

    return BotInitiator.INGAME

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "UnknownCommand")
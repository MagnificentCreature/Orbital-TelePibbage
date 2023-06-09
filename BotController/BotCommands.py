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

    await DialogueReader.sendMessageByID(context.bot, update.callback_query.from_user.id, "StartGameOption", reply_markup=BotInitiator.StartGameKeyboard)

    return BotInitiator.INROOM

async def join_room_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return BotInitiator.ENTERCODE

async def join_room_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    room_code = update.message.text
    return await join_room(update, context, room_code)

async def join_room(update: Update, context: ContextTypes.DEFAULT_TYPE, roomCode=None):
    try:
        if roomCode is None:
            roomCode = update.message.text.split(" ")[1]
    except IndexError:
        await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "RoomNotFound")
        return BotInitiator.END
    await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "JoinRoom1", **{"roomCode": roomCode})
    success = await RoomHandler.joinRoom(update.message.from_user.username, roomCode, context.bot)
    if not success:
        return BotInitiator.END

    waiting_to_start = asyncio.Event()
    context.user_data["waiting_to_start"] = waiting_to_start
    await waiting_to_start.wait()
    context.user_data['waiting_to_start'].clear()

    return BotInitiator.INGAME

async def leave_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await RoomHandler.leaveRoom(update.message.from_user.username, context.bot)

    return BotInitiator.FRESH

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = (" ").join(update.message.text.split(" ")[1:]) #TODO logic flow if invalid prompt or no prompt
    imageurl = await ImageGenerator.imageQuery(prompt)
    print(update.message.from_user.username + "Generated Image: " + str(imageurl))
    await DialogueReader.sendImageURLByID(context.bot, update.message.from_user.id, imageurl)

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await RoomHandler.startGame(update.callback_query.from_user.username, context.bot)
    return BotInitiator.INGAME

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "UnknownCommand")
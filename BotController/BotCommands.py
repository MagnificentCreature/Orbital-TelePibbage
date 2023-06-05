"""
Handles user commands
"""

import asyncio

from telegram import Update
from telegram.ext import ContextTypes

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
    await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "Welcome2")
    
    if (context.args):
        roomCode = context.args[0]
        await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "JoinRoom1", **{"roomCode": roomCode})
        await RoomHandler.joinRoom(update.message.from_user.username, roomCode, context.bot)

        return BotInitiator.INROOM
    
    return BotInitiator.FRESH

async def create_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "CreateRoom1")
    await RoomHandler.generateRoom(update.message.from_user.username, context.bot)

    return BotInitiator.INROOM

async def join_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        roomCode = update.message.text.split(" ")[1]
    except IndexError:
        await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "RoomNotFound")
        return
    await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "JoinRoom1", **{"roomCode": roomCode})
    await RoomHandler.joinRoom(update.message.from_user.username, roomCode, context.bot)

    await asyncio.Event()

    return BotInitiator.INGAME

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = (" ").join(update.message.text.split(" ")[1:]) #TODO logic flow if invalid prompt or no prompt
    imageurl = await ImageGenerator.imageQuery(prompt)
    print(update.message.from_user.username + "Generated Image: " + str(imageurl))
    await DialogueReader.sendImageURLByID(context.bot, update.message.from_user.id, imageurl)

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    return BotInitiator.INGAME

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "UnknownCommand")

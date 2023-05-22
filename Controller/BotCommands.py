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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await DialogueReader.sendMessage(context.bot, update, "Welcome1")
    await DialogueReader.sendMessage(context.bot, update, "Welcome2")

async def create_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await DialogueReader.sendMessage(context.bot, update, "CreateRoom1")
    room = RoomHandler.generateRoom(update.message.from_user.username)
    if room is None:
        await DialogueReader.sendMessage(context.bot, update, "CreateRoomFail")
        return
    await DialogueReader.sendMessage(context.bot, update, "CreateRoom2", **{'roomCode':room.getCode()})
    await DialogueReader.sendMessage(context.bot, update, "CreateRoom3", **{'roomCode':room.getCode()})
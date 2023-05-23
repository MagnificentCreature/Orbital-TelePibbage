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
    PlayersManager.recordNewPlayer(update.message.from_user.username, update.message.from_user.id)
    await DialogueReader.sendMessage(context.bot, update.message.from_user.id, "Welcome1")
    await DialogueReader.sendMessage(context.bot, update.message.from_user.id, "Welcome2")

async def create_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await DialogueReader.sendMessage(context.bot, update.message.from_user.id, "CreateRoom1")
    await RoomHandler.generateRoom(update.message.from_user.username, context.bot)

async def join_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await DialogueReader.sendMessage(context.bot, update, "JoinRoom1")
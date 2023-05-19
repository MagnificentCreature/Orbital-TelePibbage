"""
Handles user commands
"""

from telegram import Update
from telegram.ext import ContextTypes

import sys
from pathlib import Path
sys.path.insert(1, str(Path(__file__).parent.parent.absolute()))
from Chat.DialogueReader import DialogueReader

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await DialogueReader.sendMessage(context.bot, update, "Welcome1")
    await DialogueReader.sendMessage(context.bot, update, "Welcome2")
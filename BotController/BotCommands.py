"""
Handles user commands
"""

import asyncio
import time
import re

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
sys.path.insert(1, str(Path(__file__).parent.parent.absolute()))

from Player.Player import Player
from Room.Room import Room
from Chat.DialogueReader import DialogueReader
from Room.RoomHandler import RoomHandler
from Player.PlayersManager import PlayersManager
from ImageGeneration import ImageGenerator
from BotController import BotInitiator
from GameController import Lying

MIN_PROMPT_LENGTH = 3
MAX_PROMPT_LENGTH = 15

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (update.message.from_user.username is None):
        await update.message.reply_text("Please set a username before using this bot")
        return BotInitiator.END
    player = await PlayersManager.recordNewPlayer(update.message.from_user.username, update.message.from_user.id, context.user_data)
    await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "Welcome1")
    
    if (context.args):
        roomCode = context.args[0]        
        return await join_room(update, context, roomCode)
    
    await player.sendMessage(context.bot, "Welcome2", reply_markup=BotInitiator.WelcomeKeyboard)
    return BotInitiator.FRESH

async def create_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(text=DialogueReader.queryDialogue("CreateRoom1"))
    await RoomHandler.generateRoom(update.callback_query.from_user.username, context.bot)
    return BotInitiator.INROOM

async def join_room_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(text=DialogueReader.queryDialogue("EnterCode"), reply_markup=BotInitiator.ReenterKeyboard)
    return BotInitiator.ENTERCODE

async def join_room_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    room_code = str.upper(update.message.text)
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
    imageURL = await ImageGenerator.imageQuery(prompt, update.message.from_user.username) 
    print(update.message.from_user.username + "Generated Image: " + str(imageURL))
    await DialogueReader.sendImageURLByID(context.bot, update.message.from_user.id, imageURL)

async def change_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await RoomHandler.changeMode(update.callback_query.from_user.username, context.bot)
    return BotInitiator.INROOM

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await RoomHandler.startGame(update.callback_query.from_user.username, context.bot):
        return BotInitiator.INROOM
    return BotInitiator.PROMPTING_PHASE

async def take_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Check if the user is in a game
    if not context.user_data['in_game']:
        return BotInitiator.WAITING_FOR_HOST
    # TODO: handle bad prompts or failure to generate image
    #asyncio.wait_for(ImageGenerator.imageQuery(update.message).wait(), timeout=60)

    prompt = update.message.text
    # SPECIAL_CHARACTERS = ["[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "*", "!"] # [".",">","!"]
    # for eachItem in SPECIAL_CHARACTERS:
    #     prompt =  prompt.replace(eachItem, f"\{eachItem}")

    # check if prompt is less than 3 words
    if len(prompt.split(" ")) < MIN_PROMPT_LENGTH:
        await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "PromptFewWords", **{"limit": MIN_PROMPT_LENGTH})
        return BotInitiator.PROMPTING_PHASE
    
    # check if prompt exceeds limit
    if len(prompt.split(" ")) > MAX_PROMPT_LENGTH:
        await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "PromptManyWords", **{"limit": MAX_PROMPT_LENGTH})
        return BotInitiator.PROMPTING_PHASE
    
    await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "PromptRecieved")
    
    task = asyncio.create_task(ImageGenerator.imageQuery(prompt, update.message.from_user.username))
    image = await task

    if image is not None and image.getProcessing() > 0:
        eta = image.getProcessing()
        await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "PromptTakingAwhile", **{"eta": eta})
        await asyncio.sleep(eta)
        image = await ImageGenerator.fetchImage(image, update.message.from_user.username, bot=context.bot)

    if image is None:
        await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "InvalidPrompt")
        return BotInitiator.PROMPTING_PHASE

    context.user_data['prompt'] = image.getPrompt()
    # Send the image URL in a separate task
    send_image_task = asyncio.create_task(DialogueReader.sendImageURLByID(context.bot, update.message.from_user.id, image.getImageURL(), caption="You generated: " + image.getPrompt()))

    await RoomHandler.takeImage(context.user_data['roomCode'], update.message.from_user.username, image)

    await send_image_task
    waitingID = await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "WaitingForItems", **{'item': "prompt"})     #TODO find a way to delete this message when the next phase starts
    
    check_items_task = asyncio.create_task(RoomHandler.checkItems(context.user_data['roomCode'], Player.PlayerConstants.PROMPT, context.bot))
    await check_items_task
    return BotInitiator.LYING_PHASE

async def take_lie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Check if the user is in a game
    if not context.user_data['in_game']:
        return BotInitiator.WAITING_FOR_HOST
    
    # check if the room is in the lying state
    if not await RoomHandler.checkState(context.user_data['roomCode'], Room.State.LYING_STATE):
        # TODO Handle the phase error
        print("Error: Not in lying phase")
        return BotInitiator.LYING_PHASE
    
    try:
        if context.user_data['next_lie'] is not None:
            await context.user_data['next_lie'].insertLie(update.message.text, update.message.from_user.username)
            await update.message.delete()
            if not await RoomHandler.sendNextImage(context.bot, context.user_data["roomCode"], update.message.from_user.username):
                waitingID = await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "WaitingForItems", **{'item': "lie"})     #TODO find a way to delete this message when the next round starts
                await RoomHandler.checkItems(context.user_data['roomCode'], Player.PlayerConstants.LIE, context.bot)
                return BotInitiator.VOTING_PHASE
            return BotInitiator.LYING_PHASE
    except KeyError:
        print("next_lie key error")
        return BotInitiator.LYING_PHASE
    
    # TODO: handle bad lies or failure to generate image
    return BotInitiator.LYING_PHASE

async def handle_vote_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Flow control to see if the user is in a game
    try:
        if not context.user_data['in_game']:
            return BotInitiator.FRESH
    except KeyError:
        return BotInitiator.FRESH

    # Flow contorl check if the player has already voted
    if context.user_data['has_voted']:
        return BotInitiator.VOTING_PHASE
        
    query = update.callback_query
    data = re.split(r"(?<!\\):", query.data)
    lie = data[1]
    lieAuthor = data[2]
    playerTricked = update.callback_query.from_user.username

    room = RoomHandler.getRoom(context.user_data['roomCode'])
    # image_list = room.getImageList(player)

    votingImage = await room.getVotingImage()
    await votingImage.addPlayersTricked(lieAuthor, playerTricked)
    context.user_data['has_voted'] = True
    await DialogueReader.sendMessageByID(context.bot, update.callback_query.from_user.id, "WaitingForItems", **{'item': "vote"})     #TODO find a way to delete this message when the next round starts    
    
    # checkItems returns True after everyone places voe for one image
    if await room.checkItems(Player.PlayerConstants.HAS_VOTED, context.bot, advance=False):
        #reveal
        message = await votingImage.showPlayersTricked()

        await room.broadcast(context.bot, message=message, raw=True, parse_mode=DialogueReader.MARKDOWN)
        await asyncio.sleep(2)
        hasNext = await room.broadcast_voting_image(context.bot)
        if not hasNext:
            await room.advanceState(context.bot)
            await RoomHandler.endGame(context.user_data['roomCode'], context.bot)
            return BotInitiator.FRESH

    return BotInitiator.VOTING_PHASE  

async def play_again(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_reply_markup(reply_markup=None)
    oldRoomCode = update.callback_query.data.split(":")[1]
    await RoomHandler.playAgain(context.bot, update.callback_query.from_user.username, oldRoomCode)
    return BotInitiator.INROOM

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "UnknownCommand")
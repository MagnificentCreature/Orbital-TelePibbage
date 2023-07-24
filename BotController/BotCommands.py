"""
Handles user commands
"""

import asyncio
from functools import wraps
import re
from telegram import InputMediaPhoto, Update
import telegram
from telegram.ext import ContextTypes

import sys
from pathlib import Path

from Player.PlayerConstants import PlayerConstants
sys.path.insert(1, str(Path(__file__).parent.parent.absolute()))

from Room.Room import Room
from Chat.DialogueReader import DialogueReader
from Room.RoomHandler import RoomHandler
from Player.PlayersManager import PlayersManager
from ImageGeneration import ImageGenerator
from GameController import ArcadeGen
from BotController.BotInitiatorConstants import BotInitiatorConstants

MIN_PROMPT_LENGTH = 3
# MAX_PROMPT_LENGTH = 15
MAX_CHARACTERS = 80

def button_stall_decorator(func):
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        # await asyncio.sleep(0.5)S
        if context.user_data.get("pressing_button", False):
            return
        context.user_data["pressing_button"] = True
        result = await func(update, context, *args, **kwargs)
        context.user_data["pressing_button"] = False
        return result
    return wrapper

def check_in_game_decorator(func):
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        #Check if the user is in a game
        if not context.user_data['in_game']:
            return BotInitiatorConstants.WAITING_FOR_HOST
        return await func(update, context, *args, **kwargs)
    return wrapper

def timeout_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        max_retries = 5
        retry_delay = 1
        retry_count = 0
        while retry_count < max_retries:
            try:
                return await func(*args, **kwargs)
            except telegram.error.TimedOut as e:
                if retry_count >= max_retries:
                    print(f"Timed out: {str(e)} after {retry_count} retries. Giving up.")
                    raise
                else:
                    print(f"Timed out: {str(e)} running {func.__name__}. Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    retry_count += 1

        return await wrapper(*args, **kwargs)
    return wrapper

# def timeout_decorator(func):
#     @wraps(func)
#     async def wrapper(update, context, *args, **kwargs):
#         try:
#             return await func(update, context, *args, **kwargs)
#         except telegram.error.TimedOut as timeOutError:
#             print(f"Timed out running {func.__name__}\n" + str(timeOutError))
#     return wrapper

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (update.message.from_user.username is None):
        await update.message.reply_text("Please set a username before using this bot")
        return BotInitiatorConstants.END
    player = await PlayersManager.recordNewPlayer(update.message.from_user.username, update.message.from_user.id, context.user_data)
    await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "Welcome1")
    
    if (context.args):
        roomCode = context.args[0]        
        return await join_room(update, context, roomCode)
    
    await player.sendMessage(context.bot, "Welcome2", reply_markup=BotInitiatorConstants.WelcomeKeyboard)
    return BotInitiatorConstants.FRESH

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "HelpGuide", parse_mode=DialogueReader.MARKDOWN)

async def create_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(text=DialogueReader.queryDialogue("CreateRoom1"))
    await RoomHandler.generateRoom(update.callback_query.from_user.username, context.bot)
    return BotInitiatorConstants.INROOM

async def join_room_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(text=DialogueReader.queryDialogue("EnterCode"), reply_markup=BotInitiatorConstants.ReenterKeyboard)
    return BotInitiatorConstants.ENTERCODE

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
        return BotInitiatorConstants.FRESH
    
    await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "JoinRoom1", **{"roomCode": roomCode})
    success = await RoomHandler.joinRoom(update.message.from_user.username, roomCode, context.bot)
    
    if not success:
        await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "InvalidRoom")
        await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "ReenterCode", reply_markup=BotInitiatorConstants.ReenterKeyboard)
        return BotInitiatorConstants.ENTERCODE
    
    return BotInitiatorConstants.INROOM

async def return_to_fresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data['roomCode'] == "":
        await update.callback_query.edit_message_text(text=DialogueReader.queryDialogue("ReturningToStart"))
    else:
        await update.callback_query.delete_message()
        await RoomHandler.leaveRoom(update.callback_query.from_user.username, context.bot)
    await DialogueReader.sendMessageByID(context.bot, update.callback_query.from_user.id, "Welcome2", reply_markup=BotInitiatorConstants.WelcomeKeyboard)
    return BotInitiatorConstants.FRESH

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = (" ").join(update.message.text.split(" ")[1:]) #TODO logic flow if invalid prompt or no prompt
    imageURL = await ImageGenerator.imageQuery(prompt, update.message.from_user.username) 
    print(update.message.from_user.username + "Generated Image: " + str(imageURL))
    await DialogueReader.sendImageURLByID(context.bot, update.message.from_user.id, imageURL)

@button_stall_decorator
async def change_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await RoomHandler.changeMode(update.callback_query.from_user.username, context.bot)
    return BotInitiatorConstants.INROOM

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await RoomHandler.startGame(update.callback_query.from_user.username, context.bot):
        return BotInitiatorConstants.INROOM
    await update.callback_query.edit_message_reply_markup(reply_markup=None)
    if RoomHandler.getGameMode(context.user_data['roomCode']) == Room.Mode.VANILLA:
        return BotInitiatorConstants.PROMPTING_PHASE
    elif RoomHandler.getGameMode(context.user_data['roomCode']) == Room.Mode.ARCADE:
        return BotInitiatorConstants.ARCADE_GEN_PHASE

@check_in_game_decorator
@timeout_decorator
async def take_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: handle bad prompts or failure to generate image
    #asyncio.wait_for(ImageGenerator.imageQuery(update.message).wait(), timeout=60)

    # check if the room is in the prompting state
    if not await RoomHandler.checkState(context.user_data['roomCode'], Room.State.PROMPTING_STATE):
        # TODO Handle the phase error
        print("Error: Not in prompting phase")
        return BotInitiatorConstants.PROMPTING_PHASE

    prompt = update.message.text
    # SPECIAL_CHARACTERS = ["[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "*", "!"] # [".",">","!"]
    # for eachItem in SPECIAL_CHARACTERS:
    #     prompt =  prompt.replace(eachItem, f"\{eachItem}")

    # check if prompt is less than 3 words
    if len(prompt.split(" ")) < MIN_PROMPT_LENGTH:
        await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "PromptFewWords", **{"limit": MIN_PROMPT_LENGTH})
        return BotInitiatorConstants.PROMPTING_PHASE
    
    # check if prompt exceeds limit
    if len(prompt) > MAX_CHARACTERS:
        await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "PromptManyChars", **{"limit": MAX_CHARACTERS})
        return BotInitiatorConstants.PROMPTING_PHASE
    
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
        return BotInitiatorConstants.PROMPTING_PHASE

    context.user_data['prompt'] = image.getPrompt()
    # Send the image URL in a separate task
    send_image_task = asyncio.create_task(DialogueReader.sendImageURLByID(context.bot, update.message.from_user.id, image.getImageURL(), caption="You generated: " + image.getPrompt(), raw=True))

    await RoomHandler.takeImage(context.user_data['roomCode'], update.message.from_user.username, image)

    await send_image_task

    context.user_data["waiting_msg"] = await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "WaitingForItems", **{'item': "prompt"})     #TODO find a way to delete this message when the next phase starts
    
    check_items_task = asyncio.create_task(RoomHandler.checkItems(context.user_data['roomCode'], PlayerConstants.PROMPT, context.bot))
    await check_items_task
    return BotInitiatorConstants.LYING_PHASE

@check_in_game_decorator
@timeout_decorator
async def take_lie(update: Update, context: ContextTypes.DEFAULT_TYPE):    
    # check if the room is in the lying state
    if not await RoomHandler.checkState(context.user_data['roomCode'], Room.State.LYING_STATE):
        # TODO Handle the phase error
        print("Error: Not in lying phase")
        return BotInitiatorConstants.LYING_PHASE
    
    try:
        if context.user_data['next_lie'] is not None:
            # check if update.message.text is over the character limit
            # Tidy up old message
            await update.message.delete()
            if "LieTooLong" in context.user_data:
                await context.user_data["LieTooLong"].delete()
                del context.user_data["LieTooLong"] 
            
            # Check if lie is too long
            if len(update.message.text) > MAX_CHARACTERS:
                await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "LieTooLong", messageKey="LieTooLong", **{"limit": MAX_CHARACTERS})
                return BotInitiatorConstants.LYING_PHASE
            
            await context.user_data['next_lie'].insertLie(update.message.text, update.message.from_user.username)
            if not await RoomHandler.sendNextImage(context.bot, context.user_data["roomCode"], update.message.from_user.username):
                context.user_data["waiting_msg"] = await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "WaitingForItems", **{'item': "lie"})     #TODO find a way to delete this message when the next round starts
                await RoomHandler.checkItems(context.user_data['roomCode'], PlayerConstants.LIE, context.bot)
                return BotInitiatorConstants.VOTING_PHASE
            return BotInitiatorConstants.LYING_PHASE
    except KeyError:
        print("next_lie key error")
        return BotInitiatorConstants.LYING_PHASE
    
    # TODO: handle bad lies or failure to generate image
    return BotInitiatorConstants.LYING_PHASE

@button_stall_decorator
@timeout_decorator
async def handle_vote_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Flow control to see if the user is in a game
    try:
        if not context.user_data['in_game']:
            return BotInitiatorConstants.FRESH
    except KeyError:
        return BotInitiatorConstants.FRESH

    # Flow control check if the player has already voted
    if context.user_data['has_voted']:
        return BotInitiatorConstants.VOTING_PHASE
        
    query = update.callback_query
    data = re.split(r"(?<!\\):", query.data)
    lieAuthor = data[1]
    playerTricked = update.callback_query.from_user.username

    room = RoomHandler.getRoom(context.user_data['roomCode'])
    # image_list = room.getImageList(player)

    votingImage = await room.getVotingImage()
    await votingImage.addPlayersTricked(lieAuthor, playerTricked)
    context.user_data['has_voted'] = True
    context.user_data["waiting_msg"] = await DialogueReader.sendMessageByID(context.bot, update.callback_query.from_user.id, "WaitingForItems", **{'item': "vote"})     #TODO find a way to delete this message when the next round starts    
    
    # checkItems returns True after everyone places vote for one image
    if await room.checkItems(PlayerConstants.HAS_VOTED, context.bot, advance=False):
        #reveal
        message = await votingImage.showPlayersTricked()

        await room.broadcast(context.bot, message=message, raw=True, parse_mode=DialogueReader.MARKDOWN)
        await asyncio.sleep(2)
        hasNext = await room.broadcast_voting_image(context.bot)
        if not hasNext:
            await room.advanceState(context.bot)
            await RoomHandler.endGame(context.user_data['roomCode'], context.bot)
            return BotInitiatorConstants.FRESH

    return BotInitiatorConstants.VOTING_PHASE  

@button_stall_decorator
@check_in_game_decorator
@timeout_decorator
async def handle_arcade_gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # check if the room is in the arcade gen state
    if not await RoomHandler.checkState(context.user_data['roomCode'], Room.State.ARCADE_GEN_STATE):
        # TODO Handle the phase error
        print("Error: Not in arcade gen phase")
        return BotInitiatorConstants.ARCADE_GEN_PHASE
    
    query = update.callback_query
    data = re.split(r"(?<!\\):", query.data)
    prompt_string1 = data[1]
    number = data[2]
        
    if "arcade_gen_string" not in context.user_data:
        context.user_data["arcade_gen_string"] = [prompt_string1]
    elif len(context.user_data["arcade_gen_string"]) < int(number):
        context.user_data["arcade_gen_string"] += [prompt_string1]
    else:
        return
    
    if len(data) > 3:
        print("Banning " + data[3])
        context.user_data["banned_category"] = data[3]

    banned_category = context.user_data.get("banned_category")
    await ArcadeGen.recievePickedWord(update.callback_query.from_user.username, context.user_data["arcade_gen_string"], banned=banned_category)
    return BotInitiatorConstants.ARCADE_GEN_PHASE

@button_stall_decorator
@check_in_game_decorator
@timeout_decorator
async def handle_arcade_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # check if the room is in the prompting state
    if not await RoomHandler.checkState(context.user_data['roomCode'], Room.State.ARCADE_GEN_STATE):
        # TODO Handle the phase error
        print("Error: Not in arcade gen phase")
        return BotInitiatorConstants.ARCADE_GEN_PHASE

    if "arcade_prompt_list" not in context.user_data:
        return BotInitiatorConstants.ARCADE_GEN_PHASE

    await update.callback_query.edit_message_reply_markup(reply_markup=None)
    query = update.callback_query
    data = re.split(r"(?<!\\):", query.data)
    prompt = context.user_data["arcade_prompt_list"][int(data[1])]
    if context.user_data.get("prompt", False):
        return
    context.user_data['prompt'] = prompt
    
    await DialogueReader.sendMessageByID(context.bot, update.callback_query.from_user.id, "ArcadePhase1p7", **{"prompt": DialogueReader.parseFormatting(prompt)}, parse_mode=DialogueReader.MARKDOWN)
    
    task = asyncio.create_task(ImageGenerator.imageQuery(prompt, update.callback_query.from_user.username, safe=False))
    image = await task

    if image is not None and image.getProcessing() > 0:
        eta = image.getProcessing()
        await DialogueReader.sendMessageByID(context.bot, update.callback_query.from_user.id, "PromptTakingAwhile", **{"eta": eta})
        await asyncio.sleep(eta)
        image = await ImageGenerator.fetchImage(image, update.callback_query.from_user.username, bot=context.bot, arcade=True)

    # TODO: Find better way to handle case where even backup image fails (and thus returns none). NOTE Userdata prompt is set early
    if image is None:
        del context.user_data['prompt']
        del context.user_data['arcade_prompt_list']
        del context.user_data['arcade_gen_string']
        await DialogueReader.sendMessageByID(context.bot, update.callback_query.from_user.id, "PromptFailed")
        await ArcadeGen.sendRandomElements(context.bot, None, PlayersManager.queryPlayer(update.callback_query.from_user.username))
        return BotInitiatorConstants.ARCADE_GEN_PHASE

    # We do not send the image immidiately, as we want to wait for the other player to send their captions

    context.user_data["waiting_msg"] = await DialogueReader.sendMessageByID(context.bot, update.callback_query.from_user.id, "WaitingForItems", **{'item': "prompt"})
    context.user_data["arcade_image"] = image
    await RoomHandler.takeImage(context.user_data['roomCode'], update.callback_query.from_user.username, image)
    
    check_items_task = asyncio.create_task(RoomHandler.checkItems(context.user_data['roomCode'], PlayerConstants.ARCADE_IMAGE, context.bot))
    await check_items_task
    
    return BotInitiatorConstants.CAPTION_PHASE

@check_in_game_decorator
@timeout_decorator
async def take_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # check if the room is in the lying state
    if not await RoomHandler.checkState(context.user_data['roomCode'], Room.State.CAPTION_STATE):
        # TODO Handle the phase error
        print("Error: Not in caption phase")
        return BotInitiatorConstants.CAPTION_PHASE
    
    try:
        if context.user_data['next_caption'] is not None:
            await update.message.delete()
            if "CaptionTooLong" in context.user_data:
                await context.user_data["CaptionTooLong"].delete()
                del context.user_data["CaptionTooLong"] 
            
            # Check if lie is too long
            if len(update.message.text) > MAX_CHARACTERS:
                await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "CaptionTooLong", messageKey="CaptionTooLong", **{"limit": MAX_CHARACTERS})
                return BotInitiatorConstants.CAPTION_PHASE
            
            await context.user_data['next_caption'].insertCaption(update.message.text, update.message.from_user.username)
            if not await RoomHandler.sendNextImage(context.bot, context.user_data["roomCode"], update.message.from_user.username):
                context.user_data["waiting_msg"] = await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "WaitingForItems", **{'item': "caption"})     #TODO find a way to delete this message when the next round starts
                await RoomHandler.checkItems(context.user_data['roomCode'], PlayerConstants.CAPTION, context.bot)
                return BotInitiatorConstants.PICKING_PHASE
            return BotInitiatorConstants.CAPTION_PHASE
    except KeyError:
        print("next_caption key error")
        return BotInitiatorConstants.CAPTION_PHASE
    
    # TODO: handle bad lies or failure to generate image
    return BotInitiatorConstants.CAPTION_PHASE

@button_stall_decorator
@check_in_game_decorator
@timeout_decorator
async def handle_pick(update: Update, context: ContextTypes.DEFAULT_TYPE):
        
    query = update.callback_query
    data = re.split(r"(?<!\\):", query.data)
    captionNum = int(data[1])
    captionAuthor = data[2]

    #modify the image object to include the caption
    context.user_data['arcade_image'].selectCaption(captionNum, captionAuthor)

    #produce the image

    #send the new image to the player
    await update.callback_query.edit_message_media(InputMediaPhoto(context.user_data['arcade_image'].getImageURL())) #TODO: Replace with new Canvas'd image
    await DialogueReader.sendMessageByID(context.bot, update.callback_query.from_user.id, context.user_data['arcade_image'].getCaption(), raw=True)

    #check if everyone has picked
    context.user_data['has_picked'] = True
    await RoomHandler.checkItems(context.user_data['roomCode'], PlayerConstants.HAS_PICKED, context.bot)

    return BotInitiatorConstants.BATTLE_PHASE

@button_stall_decorator
@timeout_decorator
async def battle_vote_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Flow control to see if the user is in a game
    try:
        if not context.user_data['in_game']:
            return BotInitiatorConstants.FRESH
    except KeyError:
        return BotInitiatorConstants.FRESH

    # Flow control check if the player has already voted
    if context.user_data.get('has_voted', False):
        return BotInitiatorConstants.BATTLE_PHASE
    
    await update.callback_query.message.delete() # Delete the message that asks the users to vote
    query = update.callback_query
    data = re.split(r"(?<!\\):", query.data)
    voteNumber = int(data[1])
    finals = False
    if len(data) > 2:
        finals = data[2] == "True"

    room = RoomHandler.getRoom(context.user_data['roomCode'])
    
    battleImages = room.getBattleImages()
    battleImages[voteNumber].addBattleVoter(update.callback_query.from_user.username)
    context.user_data['has_voted'] = True
    # context.user_data["waiting_msg"] = await DialogueReader.sendMessageByID(context.bot, update.callback_query.from_user.id, "WaitingForItems", **{'item': "vote"})     #TODO find a way to delete this message when the next round starts
    
    # checkItems returns True after everyone places vote for one image
    if await room.checkItems(PlayerConstants.HAS_VOTED, context.bot, advance=False):
        #reveal
        if await room.advanceBattle(context.bot, finals=finals):
            await RoomHandler.endGame(context.user_data['roomCode'], context.bot)
            return BotInitiatorConstants.FRESH 
        return BotInitiatorConstants.BATTLE_PHASE

    return BotInitiatorConstants.BATTLE_PHASE

async def play_again(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_reply_markup(reply_markup=None)
    oldRoomCode = update.callback_query.data.split(":")[1]
    await RoomHandler.playAgain(context.bot, update.callback_query.from_user.username, oldRoomCode)
    return BotInitiatorConstants.INROOM

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await DialogueReader.sendMessageByID(context.bot, update.message.from_user.id, "UnknownCommand")
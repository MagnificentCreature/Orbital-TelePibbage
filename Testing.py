import requests
import json

BOT_TOKEN = '1646052721:AAH6IJRzcM1s6Cbv2WQlTaqNYMlPVEuhAHs'
CHAT_ID = "-511576030"
# file = "C:/Users/seanw/Downloads/sapl8o4hr4ca1.webp"

def sendMessage(message) :
    request = ('https://api.telegram.org/bot'+ BOT_TOKEN + '/sendMessage?chat_id=' 
           + CHAT_ID + '&text=' + message)
    print(request)
    send = requests.get(request)

def sendPhoto(path) :
    files = {
        'photo': open(path, 'rb')
    }
    request = ('https://api.telegram.org/bot'+ BOT_TOKEN + '/sendPhoto?chat_id=' 
           + CHAT_ID)
    print(request)
    send = requests.post(request, files = files)

def sendPoll(question, options) :
    request = ('https://api.telegram.org/bot'+ BOT_TOKEN + '/sendPoll?chat_id=' 
           + CHAT_ID + '&question=' + question + '&options=' + options)
    print(request)
    send = requests.get(request)

def readMessage() :
    request = ('https://api.telegram.org/bot'+ BOT_TOKEN + '/getUpdates')
    print(request)
    send = requests.get(request)
    print(send.json())

# options = json.dumps(['Baroque Obama', 'Obama dressing up as George Washington', 'Option 3', 'Use a hint LOL'])

# sendMessage("Welcome to Pibbage! Type /create_game to create a game lobby or /join <RoomCode> to join a game!")
# sendMessage("If you're new here, check <Insert youtube video/website> for the rules!")
# sendMessage("Creating game lobby...")
# sendMessage("Your room code is 4419")
# sendMessage("""Invite your friends to the room by sending them this link: https://t.me/PibbageBot?start=4419 
# OR 
# getting them to send /join 4419 to me""")
# sendMessage("Waiting for players to join... Type /start_game to start the game")
# sendMessage("@HoXuWen has joined the lobby (2/8)")
# sendMessage("@DonaldTrump has joined the lobby (3/8)")
# sendMessage("@BarackObama has joined the lobby (4/8)")

# sendMessage("Joining game lobby 4419...")
# sendMessage("Your room code is 4419")
# sendMessage("""Invite your friends to the room by sending them this link: https://t.me/PibbageBot?start=4419 
# OR 
# getting them to send /join 4419 to me""")
# sendMessage("Waiting for host to start the game...")
# sendMessage("@HoXuWen has joined the lobby (2/8)")
# sendMessage("@DonaldTrump has joined the lobby (3/8)")
# sendMessage("@BarackObama has joined the lobby (4/8)")

# sendMessage("Starting game for lobby 4419...")
# sendMessage("Prompt Round!")
# sendMessage("Send your prompts for round 1 to @PibbageBot (Click Use a Hint if you can't decide)")
# sendMessage('30 seconds left! Faster send your prompt or click "Use a Hint" if you can\'t decide!')

# sendMessage("Prompt recieved, waiting for other players...")
# sendMessage("All prompts have been recieved, generating images")

# sendMessage("Lying Round!")
# sendMessage("Enter your lies for the various photos shown! You have 30 seconds for each photo!")
# sendMessage("Photo 1:")
# sendPhoto("C:/Users/seanw/Downloads/sapl8o4hr4ca1.webp")
# sendMessage("Enter your lie for this photo, or click 'Use a Hint' if you can't decide")
# sendMessage("10 seconds left! Time to click send!")

sendMessage("Voting Round!")
sendMessage("Photo 1:")
sendPhoto("C:/Users/seanw/Downloads/sapl8o4hr4ca1.webp")
sendMessage("Vote for the prompt you think generated Photo 1!")
sendPoll("Which prompt generated Photo 1?", options)
sendMessage("Vote for the prompt you think generated Photo 1!")
sendMessage("new branch")

# sendMessage('"Baroque Obama"')
# sendMessage("Picked By: @HoXuWen")
# sendMessage("This was the TRUTH! generated by @MagnificentCreature")
# sendMessage("@HoXuWen gains +250 points!")

# sendMessage("Leaderboard:")
# sendMessage("1. @HoXuWen: 1000 points")
# sendMessage("2. @MagnificentCreature: 750 points")
# sendMessage("3. @DonaldTrump: 500 points")
# sendMessage("4. @BarackObama: 250 points")

# sendMessage("Enter your lies for this Photo")

# message = ('https://api.telegram.org/bot'+ bot_token + '/sendMessage?chat_id=' 
#            + chat_id + '&text=Enter your lies for this Photo')
# print(message)
# send = requests.get(message)


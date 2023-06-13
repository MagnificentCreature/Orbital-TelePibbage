'''
Singleton controller class that manages things to do with players in the global context
Can be later replaced with the interace that interacts with a player database
For now it will interact with a text file
'''

from os import path
# import player class
from Player.Player import Player #This import does not work when running this script directly, but works when running from main.py

CONTEXT_TEMPLATE = []

class PlayersManager:
    #Private Class variable
    _playerRecord = {}

    def __readPlayers(filepath):
        data = {}
        try:
            with open(filepath, "r") as f:
                for line in f:
                    data[line.strip().split(",")[0]] = Player(
                        line.strip().split(",")[0], line.strip().split(",")[1]
                    )
        except FileNotFoundError:
            ("Players.txt not found, creating new file")
            with open(filepath, "w") as f:
                f.write("")
        return data

    _dir_path = path.dirname(path.realpath(__file__))
    _players_path = path.join(_dir_path, "Players.txt")

    _playerRecord = __readPlayers(_players_path)

    # method that adds a player to the playerRecord
    @classmethod
    async def recordNewPlayer(cls, username, id, user_data):
        # check if player is already in the list
        if username in cls._playerRecord.keys():
            player = cls._playerRecord[username]
            # TODO better solution to this?
            player.updateUserData(user_data)
            return player
        
        # add player to list
        cls._playerRecord[username] = Player(username, id, user_data)

        # # write to file
        with open(cls._players_path, "a") as f: # is this secure?
            f.write(username + "," + str(id) + ",0\n")
        f.close()

        return cls._playerRecord[username]
    
    # TODO: method that removes a player from the player list

    # method that returns the player if he is in the dictionary, else creates a new one
    @classmethod
    def queryPlayer(cls, username):
        # check if player is already in the dicitonary
        return cls._playerRecord[username]
    
    # # returns the room code a player is in if he is in one, else return -1
    # def getRoom(username):
    #     return username.getRoomCode()
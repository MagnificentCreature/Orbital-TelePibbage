'''
Singleton controller class that manages things to do with players in the global context
Can be later replaced with the interace that interacts with a player database
For now it will interact with a text file
'''

from os import path
# import player class
from Player.Player import Player #This import does not work when running this script directly, but works when running from main.py

class PlayersManager:
    playerRecord = {}

    file_path = path.realpath(__file__)
    dir_path = path.dirname(file_path)
    players_path = path.join(dir_path, "Players.txt")

    with open(players_path, "r") as f:
        for line in f:
            playerRecord[line.strip().split(",")[0]] = Player(
                line.strip().split(",")[0], line.strip().split(",")[1]
            )
    f.close()

    # method that adds a player to the playerRecord
    @staticmethod
    async def recordNewPlayer(username, id):
        # check if player is already in the list
        if username in PlayersManager.playerRecord.keys():
            return PlayersManager.playerRecord[username]
        
        print("Adding new player " + username + " to player list")

        # add player to list
        PlayersManager.playerRecord[username] = Player(username, id)

        # # write to file
        with open(PlayersManager.players_path, "a") as f: # is this secure?
            f.write(username + "," + str(id) + ",0\n")
        f.close()

        return PlayersManager.playerRecord[username]
    
    # method that removes a player from the player list


    # method that returns the player if he is in the dictionary, else creates a new one
    @staticmethod
    def getPlayer(player):
        # check if player is already in the dicitonary
        if player in PlayersManager.playerRecord.keys():
            return PlayersManager.playerRecord[player]
        return PlayersManager.recordNewPlayer(player)
    
    #Method is only used in DialogueReader
    def getChatID(username):
        return PlayersManager.playerRecord[username].getChatID()
    
    @staticmethod
    def isPlayerFree(username):
        return PlayersManager.playerRecord[username].isInGame()

    # # returns the room code a player is in if he is in one, else return -1
    # def getRoom(username):
    #     return username.getRoomCode()
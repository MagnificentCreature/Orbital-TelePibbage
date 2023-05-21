'''
Controller class that manages things to do with players
Can be later replaced with the interace that interacts with a player database
For now it will interact with a text file
'''

class PlayersManager:
    playerList = []

    def __init__(self):
        # initlaise player list from players.txt in name, score
        self.playerList = []
        with open("Players/players.txt", "r") as f:
            for line in f:
                self.playerList.append(line.strip().split(","))
        f.close()

    # method that adds a player to the player list
    def addPlayer(self, username):
        # check if player is already in the list
        for player in self.playerList:
            if player[0] == username:
                return False
        # add player to list
        self.playerList.append([username, 0])

        # write to file
        with open("Players/players.txt", "a") as f:
            f.write(username + ",0\n")
        f.close()

        return True
    
    # method that removes a player from the player list


    # method that returns the player if he is in the list, else creates a new one
    def getPlayer(self, username):
        for player in self.playerList:
            if player[0] == username:
                return player
        self.addPlayer(username)
        return self.getPlayer(username)
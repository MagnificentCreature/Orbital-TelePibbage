'''
Player object, identified by his unique username.
Stores information about his username, scores etc
Can later be linked to a database to keep track of (leaderboard/overall scores)
'''

class Player:
    username = ""
    score = 0
    inGame = False
    isHost = False

    def __init__(self, username):
        self.username = username
        self.score = 0
        self.inGame = False
        self.isHost = False

    def isInRoom(self):
        return self.inGame
    
    def isHost(self):
        return self.isHost
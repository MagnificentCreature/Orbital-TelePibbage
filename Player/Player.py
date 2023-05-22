'''
Player object, identified by his unique username.
Stores information about his username, scores etc
Can later be linked to a database to keep track of (leaderboard/overall scores)
'''

class Player:
    username = ""
    score = 0
    inGame = False
    roomCode = -1

    def __init__(self, username, score=0):
        self.username = username
        self.score = score
        self.inGame = False
        self.isHost = False

    def isInRoom(self):
        return self.inGame
    
    def isHost(self):
        return False
    
    def getScore(self):
        return self.score
    
class Host(Player):
    def __init__(self, username, score=0):
        super().__init__(username, score)
    
    def isHost(self):
        return True
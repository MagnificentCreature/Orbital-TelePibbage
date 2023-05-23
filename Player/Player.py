'''
Player object, identified by his unique username.
Stores information about his username, scores etc
Can later be linked to a database to keep track of (leaderboard/overall scores)
'''

class Player:
    username = ""
    chatID = 0
    score = 0
    inGame = False
    
    #roomCode = -1

    def __init__(self, username, chatID=0, score=0):
        self.username = username
        self.chatID = chatID
        self.score = score
        self.inGame = False
        
    def isInGame(self):
        return self.inGame
    
    def isHost(self):
        return False
    
    def getScore(self):
        return self.score
    
    def getChatID(self):
        return self.chatID
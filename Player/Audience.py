from Player.Player import Player


class Audience(Player):
    def __init__(self, username, score=0):
        super().__init__(username, score)
    
    def isHost(self):
        return False
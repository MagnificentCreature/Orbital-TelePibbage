from Player.Player import Player


class Host(Player):
    def __init__(self, username, score=0):
        super().__init__(username, score)
    
    def isHost(self):
        return True
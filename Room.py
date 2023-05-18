"""
Class that holds data about rooms
"""

import random

class Room:
    code = ""
    host = ""
    players = []

    def __init__(self, room, host):
        self.code = room
        self.host = host
        self.players.append(host)

    def getCode(self):
        return self.code
    
    # Add player to room
    # Fails if is already in or if room is full
    def addPlayer(self, player):
        if player in self.players or len(self.players) == 8:
            return False
        self.players.append(player)
        return True

    # Remove player from room
    # Fails if not in room or is Host
    def removePlayer(self, player):
        if player not in self.players or player == self.host:
            return False
        self.players.remove(player)
        return True

    def getPlayers(self):
        return self.players
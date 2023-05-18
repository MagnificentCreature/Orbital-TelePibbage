'''
Class that generates, deletes and holds data about rooms
'''

import random

from Room import Room

class RoomHandler:
    #hashset of rooms by their room code
    rooms = {}

    #method that initializes the room handler
    def __init__(self):
        self.rooms = {}

    #Static method that generates a random room code
    def generateRoomCode():
        code = ""
        for i in range(4):
            code += str(random.randint(0, 9))
        return code

    def generateRoom(self, host):
        #keep generating room codes while making sure there is no duplicate room codes
        code = RoomHandler.generateRoomCode()
        while code in self.rooms:
            code = RoomHandler.generateRoomCode()
        #create room and add to rooms
        self.rooms[code] = Room(code, host)
        return Room(code, host)

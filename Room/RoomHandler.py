'''
Class that generates, deletes and holds data about rooms
Information passed into rooms are given only as the usernames
So keeping track of who is in which room is important, and each player can only be in one room at a time
'''

import random

from Room import Room

class RoomHandler:
    #hashset of rooms by their room code
    rooms = {}

    #method that initializes the room handler
    def __init__(self):
        self.rooms = {}

    #Static method that generates a random four alphabet room code
    @staticmethod
    def generateRoomCode():
        code = ""
        for i in range(4):
            code += str(random.randint(0, 9))
        return code

    def generateRoom(self, host):
        # first check if host player is already in a room
        if host.isInRoom():
            return False #TODO return error code for bot to print if it failed (with reason)

        #keep generating room codes while making sure there is no duplicate room codes
        code = RoomHandler.generateRoomCode()
        while code in self.rooms:
            code = RoomHandler.generateRoomCode()
        #create room and add to rooms
        self.rooms[code] = Room(code, host)
        return Room(code, host)
    
    #method that deletes a room
    def deleteRoom(self, room):
        del self.rooms[room.getCode()]

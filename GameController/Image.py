'''
This class will store data about a given image and its associated lies
'''
class Image:
    author = "a" #store author
    prompt = "a"
    imageURL = "a" #store imageURL
    imageLies = [] #store imageLies as a tuple of (lie, player)

    async def __init__(self, author, prompt, imageURL):
        self.author = author
        self.prompt = prompt
        self.imageURL = imageURL
        self.imageLies = []

    # for each image, add a tuple for lies given by other players
    async def insertLie(self, lie, username):
        self.imageLies.append((lie, username))

        


    
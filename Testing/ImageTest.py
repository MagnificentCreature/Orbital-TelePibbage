import unittest
from unittest.mock import patch

import sys
sys.path.append('.')
from GameController.Image import Image
from Player.Player import Player

class TestImage(unittest.TestCase):
    
    def setUp(self):
        self.image = Image(author="John Doe", prompt="Cats and Dogs", imageURL="http://example.com/sample.jpg")
        self.player = Player(username="John Doe", chatID=12345)
        self.player_other = Player(username="Jane Smith", chatID=67890)

    def test_get_image_URL(self):
        # Test that getImageURL returns the correct value
        assert self.image.getImageURL() == "http://example.com/sample.jpg"

    def test_get_author(self):
        # Test that getAuthor returns the correct value
        assert self.image.getAuthor() == "John Doe"

    def test_get_prompt(self):
        # Test that getPrompt returns the correct value
        assert self.image.getPrompt() == "Cats and Dogs"

    @patch('ArcadeGenTest.PlayersManager.queryPlayer')
    async def test_insert_lie(self, mock_queryPlayer):
        # Set up the mock object
        mock_queryPlayer.return_value = self.player

        # Test that insertLie behaves correctly
        await self.image.insertLie("This is a lie", self.player.getUsername())

        # Check that the lie was inserted correctly
        self.assertEqual(self.image.imageLies[self.player.getUsername()], ("This is a lie", []))

    @patch('ArcadeGenTest.PlayersManager.queryPlayer')
    async def test_insert_caption(self, mock_queryPlayer):
        # Set up the mock object
        mock_queryPlayer.return_value = self.player

        # Test that insertCaption behaves correctly
        await self.image.insertCaption("This is a caption", self.player.getUsername())

        # Check that the caption was inserted correctly
        self.assertIn(("This is a caption", self.player.getUsername()), self.image.imageCaptions)

    @patch('ArcadeGenTest.PlayersManager.queryPlayer')
    async def test_add_players_tricked(self, mock_queryPlayer):
        # Set up the mock objects
        mock_queryPlayer.side_effect = [self.player, self.player_other]

        # First, insert a lie
        await self.image.insertLie("This is a lie", self.player.getUsername())

        # Now, add a player who was tricked by the lie
        await self.image.addPlayersTricked(self.player.getUsername(), self.player_other.getUsername())

        # Check that the player was added to the list of players tricked by the lie
        self.assertIn(self.player_other.getUsername(), self.image.imageLies[self.player.getUsername()][1])


    # Add more methods as needed...

if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import Mock, patch

import sys
sys.path.append('.')
from GameController.Image import Image
from Player.Player import Player


class TestImage(unittest.TestCase):
    
    def setUp(self):
        self.image = Image(author="John Doe", prompt="Cats and Dogs", imageURL="http://example.com/sample.jpg")
        self.player = Player(username="John Doe", chatID=12345)
        self.player2 = Player(username="Jane Smith", chatID=67890)

    def test_get_image_URL(self):
        # Test that getImageURL returns the correct value
        assert self.image.getImageURL() == "http://example.com/sample.jpg"

    def test_get_author(self):
        # Test that getAuthor returns the correct value
        assert self.image.getAuthor() == "John Doe"

    def test_get_prompt(self):
        # Test that getPrompt returns the correct value
        assert self.image.getPrompt() == "Cats and Dogs"

    #Mock the queryPlayer method from PlayersManager
    @patch('ArcadeGenTest.PlayersManager.queryPlayer')
    async def test_insert_lie(self, mock_queryPlayer):
        mock_queryPlayer.return_value = self.player
        await self.image.insertLie("This is a lie", self.player.getUsername())

        # Check that the lie was inserted correctly
        self.assertEqual(self.image.imageLies[self.player.getUsername()], ("This is a lie", []))

    @patch('ArcadeGenTest.PlayersManager.queryPlayer')
    async def test_insert_caption(self, mock_queryPlayer):
        mock_queryPlayer.return_value = self.player
        await self.image.insertCaption("This is a caption", self.player.getUsername())

        # Check that the caption was inserted correctly
        self.assertIn(("This is a caption", self.player.getUsername()), self.image.imageCaptions)

    @patch('ArcadeGenTest.PlayersManager.queryPlayer')
    async def test_add_players_tricked(self, mock_queryPlayer):
        mock_queryPlayer.side_effect = [self.player, self.player2]
        await self.image.insertLie("This is a lie", self.player.getUsername())

        # Add a player who was tricked by the lie
        await self.image.addPlayersTricked(self.player.getUsername(), self.player2.getUsername())

        # Check that the player was added to the list of players tricked by the lie
        self.assertIn(self.player2.getUsername(), self.image.imageLies[self.player.getUsername()][1])

        async def test_getCaptionKeyboard(self):
        # First, insert a caption
            await self.image.insertCaption("This is a caption", self.player.getUsername())

        # Get the caption keyboard
        caption_keyboard = self.image.getCaptionKeyboard()

        # Check the structure of the caption keyboard
        self.assertIsInstance(caption_keyboard, Mock)
        self.assertIn(("This is a caption", self.player.getUsername()), caption_keyboard)

    async def test_getInlineKeyboard(self):
        # First, insert a lie
        await self.image.insertLie("This is a lie", self.player.getUsername())

        # Get the inline keyboard
        inline_keyboard = self.image.getInlineKeyboard(self.player.getUsername())

        # Check the structure of the inline keyboard
        self.assertIsInstance(inline_keyboard, Mock)
        self.assertIn(("This is a lie", self.player.getUsername()), inline_keyboard)


if __name__ == "__main__":
    unittest.main()

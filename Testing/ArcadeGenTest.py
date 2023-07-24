import unittest
from unittest.mock import patch, mock_open
import pandas as pd

from GameController.ArcadeGen import process_generation_poll, process_prepositions

class TestProcessGenerationPoll(unittest.TestCase):
    def test_process_generation_poll(self):
        SAMPLE_PROMPT_POOL = 'Assets\PromptsGenerationPool Sample.csv'
        # Prepare a mock DataFrame by readin from the file
        df = pd.read_csv(SAMPLE_PROMPT_POOL)

        # Call the function with the mock DataFrame
        result = process_generation_poll(df)

        # Check the result
        expected_result = {
            ('Color', 10): {
                ('Grayscale', 3): ['white', 'black', 'light gray', 'dark gray'],
                ('Colors', 2): ['maroon', 'red', 'orange', 'yellow']
            },
            ('Medium', 20): {
                ('Art Movements', 1): ['abstract expressionist art style', 'art deco style', 'art nouveau style', 'avant-garde art style', 'baroque art style', 'bauhaus art style', 'color field art style', 'conceptual art style', 'constructivism art style'],                # Add other subgroups and elements for the 'Medium' column
            },
        }
        
        self.assertEqual(result, expected_result)

class TestProcessPrepositions(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open, read_data='in, on, at, to, for')
    def test_process_prepositions(self, mock_file):
        result = process_prepositions()
        expected_result = ['in', ' on', ' at', ' to', ' for']
        self.assertEqual(result, expected_result)

if __name__ == "__main__":
    unittest.main()

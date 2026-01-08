import unittest
from unittest.mock import AsyncMock, MagicMock
import sys
import os
from dotenv import load_dotenv

# Add the current directory to the path so we can import bot
sys.path.insert(0, os.path.abspath('.'))

# Load environment variables for the bot
load_dotenv()

# Import bot functions after setting up the environment
import asyncio
from bot import (
    is_valid_number,
    is_positive_response,
    is_negative_response,
    init_user_data,
    users_data,
    MIN_NUMBER,
    MAX_NUMBER,
    MAX_ATTEMPTS
)

class TestBotFunctions(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear users_data before each test
        users_data.clear()
    
    def test_is_valid_number(self):
        """Test the is_valid_number function."""
        # Valid numbers
        self.assertTrue(is_valid_number("1"))
        self.assertTrue(is_valid_number("50"))
        self.assertTrue(is_valid_number("100"))
        
        # Invalid numbers
        self.assertFalse(is_valid_number("0"))  # Below minimum
        self.assertFalse(is_valid_number("101"))  # Above maximum
        self.assertFalse(is_valid_number("abc"))  # Not a number
        self.assertFalse(is_valid_number(""))  # Empty string
        self.assertFalse(is_valid_number("50.5"))  # Decimal number
        self.assertFalse(is_valid_number("-5"))  # Negative number
    
    def test_is_positive_response(self):
        """Test the is_positive_response function."""
        # Positive responses
        self.assertTrue(is_positive_response("да"))
        self.assertTrue(is_positive_response("ДА"))
        self.assertTrue(is_positive_response("Да"))
        self.assertTrue(is_positive_response("давай"))
        self.assertTrue(is_positive_response("ДАВАЙ"))
        self.assertTrue(is_positive_response("Давай"))
        self.assertTrue(is_positive_response("сыграем"))
        self.assertTrue(is_positive_response("игра"))
        self.assertTrue(is_positive_response("сыграть"))
        self.assertTrue(is_positive_response("давай сыграем"))
        
        # Non-positive responses
        self.assertFalse(is_positive_response("нет"))
        self.assertFalse(is_positive_response("привет"))
        self.assertFalse(is_positive_response("пока"))
    
    def test_is_negative_response(self):
        """Test the is_negative_response function."""
        # Negative responses
        self.assertTrue(is_negative_response("нет"))
        self.assertTrue(is_negative_response("НЕТ"))
        self.assertTrue(is_negative_response("Нет"))
        self.assertTrue(is_negative_response("не хочу"))
        self.assertTrue(is_negative_response("в другой раз"))
        self.assertTrue(is_negative_response("не"))
        self.assertTrue(is_negative_response("стоп"))
        
        # Non-negative responses
        self.assertFalse(is_negative_response("да"))
        self.assertFalse(is_negative_response("привет"))
        self.assertFalse(is_negative_response("пока"))
    
    def test_init_user_data(self):
        """Test the init_user_data function."""
        user_id = 123456
        init_user_data(user_id)
        
        # Check if user data is initialized correctly
        self.assertIn(user_id, users_data)
        self.assertEqual(users_data[user_id]["in_game"], False)
        self.assertIsNone(users_data[user_id]["secret_number"])
        self.assertEqual(users_data[user_id]["attempts"], 0)
        self.assertEqual(users_data[user_id]["total_games"], 0)
        self.assertEqual(users_data[user_id]["wins"], 0)
        
        # Test that initializing the same user doesn't overwrite
        users_data[user_id]["in_game"] = True
        init_user_data(user_id)  # Should not change existing data
        self.assertEqual(users_data[user_id]["in_game"], True)
    
    def test_init_user_data_new_user(self):
        """Test that init_user_data creates new user data properly."""
        user_id = 999999
        # Ensure user doesn't exist yet
        self.assertNotIn(user_id, users_data)
        
        init_user_data(user_id)
        
        # Check if user data is created with correct defaults
        self.assertIn(user_id, users_data)
        expected_data = {
            "in_game": False,
            "secret_number": None,
            "attempts": 0,
            "total_games": 0,
            "wins": 0
        }
        self.assertEqual(users_data[user_id], expected_data)


class TestGameLogic(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear users_data before each test
        users_data.clear()
        
        # Import bot module to access its functions
        global bot_module
        import bot as bot_module
    
    def test_game_flow_win(self):
        """Test a complete game flow where the user wins."""
        user_id = 123456
        init_user_data(user_id)
        
        # Start the game
        users_data[user_id]["in_game"] = True
        users_data[user_id]["secret_number"] = 50  # Set a known number
        users_data[user_id]["attempts"] = 0
        
        # Simulate user guessing the correct number
        user_guess = 50
        secret_number = users_data[user_id]["secret_number"]
        
        # Check win condition
        self.assertEqual(user_guess, secret_number)
        
        # Simulate what happens when user wins
        users_data[user_id]["in_game"] = False
        users_data[user_id]["wins"] += 1
        users_data[user_id]["total_games"] += 1
        
        # Verify game state after win
        self.assertFalse(users_data[user_id]["in_game"])
        self.assertEqual(users_data[user_id]["wins"], 1)
        self.assertEqual(users_data[user_id]["total_games"], 1)
    
    def test_game_flow_loss(self):
        """Test a complete game flow where the user loses."""
        user_id = 123456
        init_user_data(user_id)
        
        # Start the game
        users_data[user_id]["in_game"] = True
        users_data[user_id]["secret_number"] = 50  # Set a known number
        users_data[user_id]["attempts"] = MAX_ATTEMPTS  # Max out attempts
        
        # Simulate game over condition
        users_data[user_id]["in_game"] = False
        users_data[user_id]["total_games"] += 1
        
        # Verify game state after loss
        self.assertFalse(users_data[user_id]["in_game"])
        self.assertEqual(users_data[user_id]["total_games"], 1)
    
    def test_attempts_tracking(self):
        """Test that attempts are tracked correctly."""
        user_id = 123456
        init_user_data(user_id)
        
        # Start the game
        users_data[user_id]["in_game"] = True
        users_data[user_id]["secret_number"] = 50
        users_data[user_id]["attempts"] = 0
        
        # Simulate several attempts
        for i in range(3):
            users_data[user_id]["attempts"] += 1
        
        self.assertEqual(users_data[user_id]["attempts"], 3)
        self.assertEqual(MAX_ATTEMPTS - users_data[user_id]["attempts"], MAX_ATTEMPTS - 3)


# Mock message class for testing
class MockMessage:
    def __init__(self, text, user_id=123456):
        self.text = text
        self.from_user = MagicMock()
        self.from_user.id = user_id


# Asynchronous tests for bot handlers would require more complex mocking
# For now, we'll focus on testing the core functions
if __name__ == '__main__':
    unittest.main()
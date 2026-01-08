# Telegram Bot "Guess the Number" 

This is a Telegram bot built with the aiogram 3 framework that allows users to play the "Guess the Number" game.

## Features

- Players try to guess a number between 1 and 100
- Each player gets 10 attempts per game
- Game state tracking (in-game or not in-game)
- Win/loss statistics per user
- Support for multiple simultaneous players

## Commands

- `/start` - Start the bot and get a welcome message
- `/help` - Get game rules and command descriptions
- `/stat` - View your game statistics
- `/cancel` - End the current game

## Game Flow

1. User starts the bot with `/start`
2. User can send "Да", "Давай", "Сыграем" or similar to start a game
3. Bot generates a random number between 1-100
4. User tries to guess the number with 10 attempts max
5. After each guess, bot tells if the secret number is higher or lower
6. Game ends when user guesses correctly or runs out of attempts

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Make sure you have your bot token in the `.env` file:
   ```
   BOT_TOKEN=your_token_here
   ```

3. Run the bot:
   ```bash
   python bot.py
   ```

## Testing

Run the tests with:
```bash
python -m unittest test_bot.py
```

or

```bash
python -m pytest test_bot.py
```

## Files

- `bot.py` - Main bot implementation
- `test_bot.py` - Unit tests for the bot
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (including bot token)

## Technical Details

- Uses aiogram 3 framework for Telegram Bot API interaction
- Stores user game data in memory (would use database in production)
- Implements all game logic as specified in requirements
- Includes comprehensive unit tests
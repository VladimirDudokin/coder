import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Game constants
MAX_ATTEMPTS = 10  # Maximum number of attempts per game
MIN_NUMBER = 1      # Minimum number to guess
MAX_NUMBER = 100    # Maximum number to guess

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Game data storage (in a real application, you might want to use a database)
users_data = {}

# Initialize user data
def init_user_data(user_id: int):
    if user_id not in users_data:
        users_data[user_id] = {
            "in_game": False,
            "secret_number": None,
            "attempts": 0,
            "total_games": 0,
            "wins": 0
        }

# Check if user message is a number in the valid range
def is_valid_number(text: str) -> bool:
    try:
        number = int(text)
        return MIN_NUMBER <= number <= MAX_NUMBER
    except ValueError:
        return False

# Check if user wants to play
def is_positive_response(text: str) -> bool:
    positive_responses = ["да", "давай", "сыграем", "игра", "сыграть", "давай сыграем"]
    return text.lower() in positive_responses

# Check if user doesn't want to play
def is_negative_response(text: str) -> bool:
    negative_responses = ["нет", "не хочу", "в другой раз", "не", "стоп"]
    return text.lower() in negative_responses

# Start command handler
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    
    await message.answer(
        "Привет! 🎮 Я бот для игры в 'Угадай число'.\n\n"
        "Я загадаю число от 1 до 100, а ты попробуй его отгадать!\n\n"
        "Отправь 'Да' или 'Давай', чтобы начать игру, или /help для подробных правил."
    )

# Help command handler
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    
    help_text = (
        "🎮 Правила игры 'Угадай число':\n\n"
        "1. Я загадываю число от 1 до 100.\n"
        "2. У тебя есть 10 попыток, чтобы отгадать его.\n"
        "3. После каждой попытки я скажу, больше или меньше загаданное число.\n\n"
        "Команды:\n"
        "/start - начать бота\n"
        "/help - показать правила\n"
        "/stat - посмотреть статистику\n"
        "/cancel - завершить текущую игру\n\n"
        "Чтобы начать игру, просто скажи 'Да' или 'Давай'!"
    )
    
    await message.answer(help_text)

# Statistics command handler
@dp.message(Command("stat"))
async def cmd_stat(message: types.Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    
    user_stats = users_data[user_id]
    total_games = user_stats["total_games"]
    wins = user_stats["wins"]
    
    if total_games == 0:
        stat_text = "Ты еще не сыграл ни одной игры. Хочешь сыграть?"
    else:
        win_rate = round((wins / total_games) * 100, 1) if total_games > 0 else 0
        stat_text = (
            f"📊 Твоя статистика:\n\n"
            f"Всего игр: {total_games}\n"
            f"Побед: {wins}\n"
            f"Процент побед: {win_rate}%\n\n"
            f"Хочешь сыграть еще?"
        )
    
    await message.answer(stat_text)

# Cancel command handler
@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    
    if users_data[user_id]["in_game"]:
        users_data[user_id]["in_game"] = False
        await message.answer(
            "Игра закончена. 🎮\n\n"
            "Если захочешь поиграть снова, просто скажи 'Да' или 'Давай'!"
        )
    else:
        await message.answer("Мы сейчас не в игре. Хочешь сыграть?")

# Main message handler
@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    init_user_data(user_id)
    
    text = message.text.lower().strip()
    
    # If user is in game
    if users_data[user_id]["in_game"]:
        # Check if user sent a number
        if is_valid_number(text):
            user_number = int(text)
            secret_number = users_data[user_id]["secret_number"]
            attempts_left = MAX_ATTEMPTS - users_data[user_id]["attempts"]
            
            # Increase attempts counter
            users_data[user_id]["attempts"] += 1
            attempts_left -= 1
            
            # Check if user guessed the number
            if user_number == secret_number:
                users_data[user_id]["in_game"] = False
                users_data[user_id]["wins"] += 1
                users_data[user_id]["total_games"] += 1
                
                await message.answer(
                    f"🎉 Поздравляю! Ты угадал число {secret_number}!\n\n"
                    f"Ты выиграл! 🏆\n\n"
                    f"Хочешь сыграть еще?"
                )
            elif user_number < secret_number:
                if attempts_left > 0:
                    await message.answer(
                        f"📈 Загаданное число больше.\n\n"
                        f"Осталось попыток: {attempts_left}"
                    )
                else:
                    users_data[user_id]["in_game"] = False
                    users_data[user_id]["total_games"] += 1
                    await message.answer(
                        f"💔 У тебя закончились попытки. Я загадал число {secret_number}.\n\n"
                        f"Попробуешь еще раз?"
                    )
            else:  # user_number > secret_number
                if attempts_left > 0:
                    await message.answer(
                        f"📉 Загаданное число меньше.\n\n"
                        f"Осталось попыток: {attempts_left}"
                    )
                else:
                    users_data[user_id]["in_game"] = False
                    users_data[user_id]["total_games"] += 1
                    await message.answer(
                        f"💔 У тебя закончились попытки. Я загадал число {secret_number}.\n\n"
                        f"Попробуешь еще раз?"
                    )
        elif text == "/cancel":
            await cmd_cancel(message)
        else:
            await message.answer(
                f"🔢 По правилам игры ты можешь присылать только числа от {MIN_NUMBER} до {MAX_NUMBER} "
                f"или команду /cancel.\n\n"
                f"Осталось попыток: {MAX_ATTEMPTS - users_data[user_id]['attempts']}"
            )
    else:  # User is not in game
        if is_positive_response(text):
            # Start new game
            users_data[user_id]["in_game"] = True
            users_data[user_id]["secret_number"] = random.randint(MIN_NUMBER, MAX_NUMBER)
            users_data[user_id]["attempts"] = 0
            
            await message.answer(
                f"🎮 Отлично! Я загадал число от {MIN_NUMBER} до {MAX_NUMBER}. "
                f"У тебя есть {MAX_ATTEMPTS} попыток, чтобы его отгадать.\n\n"
                f"Введи свое первое предположение!"
            )
        elif is_negative_response(text):
            await message.answer(
                "Жаль 😢 Если захочешь поиграть, просто скажи 'Да' или 'Давай'!"
            )
        elif text == "/stat":
            await cmd_stat(message)
        elif text == "/help":
            await cmd_help(message)
        else:
            await message.answer(
                "Я не понимаю тебя 😕\n\n"
                "Хочешь сыграть в 'Угадай число'? Скажи 'Да' или 'Давай'!"
            )

# Run the bot
async def main():
    print("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
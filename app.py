from chessdotcom import get_player_stats, get_player_profile, get_leaderboards, get_current_daily_puzzle, Client
from flask import Flask, request, jsonify
from telebot import types, TeleBot
from dotenv import load_dotenv
import requests
import logging
import time
import re
import os


logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

handlers = [logging.StreamHandler(), logging.FileHandler('logs.log')]
formatter = logging.Formatter('%(levelname)s | %(name)s | %(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

for handler in handlers:
    handler.setLevel('DEBUG')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


load_dotenv('.env')
EMAIL: str = os.getenv('EMAIL')
TOKEN: str = os.getenv('BOT_TOKEN')
BOT_NAME: str = os.getenv('BOT_NAME')
WEBHOOK_URL: str = os.getenv('BOT_WEBHOOK')

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
waiting_for_nick_profile = False
waiting_for_nick_stats = False
app = Flask(__name__)
bot = TeleBot(TOKEN)


Client.request_config["headers"]["User-Agent"] = (
    "My Python Application. "
    f"Contact me at {EMAIL}"
)


@app.route(f"/chess-webhook", methods=['POST'])
def receive_update():
    update = types.Update.de_json(request.get_json())
    logger.info('Received update from webhook')

    bot.process_new_updates([update])
    logger.info('Update processed')

    return jsonify({"status": "ok"}), 200


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Hi! I can check your stats from Chess.com /stats"
                                      " or show you today's puzzle /puzzle !\n\n"
                                      "stats - shows your stats\n"
                                      "start - shows start message with commands\n"
                                      "profile - shows your profile info\n"
                                      "puzzle - shows today's puzzle\n"
                                      "solve - shows solving moves\n"
                                      "leaders - shows leaders at categories\n")
    logger.info('Start message has been sent')


@bot.message_handler(commands=['profile', 'stats'])
def message_reply(message):

    if message.text == '/stats':
        global waiting_for_nick_stats
        waiting_for_nick_stats = True
    else:
        global waiting_for_nick_profile
        waiting_for_nick_profile = True

    bot.reply_to(message, "What's your nickname on Chess.com?", reply_markup=markup)
    logger.info('Waiting for the reply')


@bot.message_handler(commands=['puzzle'])
def show_puzzle(message):

    data = get_current_daily_puzzle().json['puzzle']
    bot.send_photo(message.chat.id, data['image'])

    bot.send_message(message.chat.id, f'Name of puzzle: {data["title"]}')
    bot.send_message(message.chat.id, 'To show answer use command /solve')

    # using FEN you can tell which color makes move b=black w=white
    fen = get_current_daily_puzzle().json['puzzle']['fen']
    move = re.search(r'\s[bw]\s', fen).group()
    if move == ' w ':
        bot.send_message(message.chat.id, 'White to Move')
    else:
        bot.send_message(message.chat.id, 'Black to Move')

    logger.info('Puzzle has been sent')


@bot.message_handler(commands=['solve'])
def solve_puzzle(message):

    # using PGN you can find solving positions
    pgn = get_current_daily_puzzle().json['puzzle']['pgn'].replace('\r\n', ' ')
    pattern = r'\s\d+\.{1,3}\s'
    start = re.search(pattern, pgn)

    solve_moves = pgn[start.start():]
    moves = re.split(pattern, solve_moves)

    for idx, element in enumerate(moves[1:]):
        move = f'{idx+1}.   {element}'
        bot.send_message(message.chat.id, move, reply_markup=markup)

    logger.info('Solution has been sent')


@bot.message_handler(commands=['leaders'])
def message_reply(message):

    data = get_leaderboards().json['leaderboards']
    categories = data.keys()

    for category in categories:
        category_string = f'Category: ' \
                          f'{category[5:].capitalize() if category.startswith("live_") else category.capitalize()}\n'
        if category == 'live_bughouse':
            break
        for idx, entry in enumerate(data[category]):
            if idx == 3:
                break
            category_string += f'Rank: {idx + 1} | Username: {entry["username"]}   |   Rating: {entry["score"]}\n'

        bot.send_message(message.chat.id, category_string)

    logger.info('Leaders have been sent')


# User's data can be without some categories because he didn't play much, so program checks it
@bot.message_handler(func=lambda message: True)
def give_stats_profile(message):

    global waiting_for_nick_profile
    global waiting_for_nick_stats

    try:

        if waiting_for_nick_stats:
            username = message.text

            data = get_player_stats(username).json
            categories = ['chess_bullet', 'chess_blitz', 'chess_rapid', 'chess_daily']

            for category in categories:
                if category in data["stats"]:
                    stats = data["stats"][category]
                    record = stats["record"]

                    # If user has played only one game or 0, stats["best"]["rating"] is not exist
                    bot.send_message(message.chat.id,
                                     f'Category: {category[6:].capitalize()}\n'
                                     f'Current: {stats["last"]["rating"]}\n'
                                     f'Best: {stats.get("best", {}).get("rating", stats["last"]["rating"])}\n'
                                     f'Games:    Win - {record["win"]} | Draw - {record["draw"]} | '
                                     f'Loss - {record["loss"]}',
                                     reply_markup=markup)

            puzzle_rush = data["stats"]["puzzle_rush"].get("best", {})
            bot.send_message(message.chat.id,
                             f'Category: Puzzle Rush\n'
                             f'Total attempts: {puzzle_rush.get("total_attempts", 0)}\n'
                             f'Best score: {puzzle_rush.get("score", 0)}', reply_markup=markup)

            waiting_for_nick_stats = False

            logger.info('Stats have been sent')

        elif waiting_for_nick_profile:

            username = message.text
            data = get_player_profile(username).json["player"]

            if data.get('avatar') is None:
                bot.send_message(message.chat.id, 'Avatar is missing', reply_markup=markup)
            else:
                bot.send_photo(message.chat.id, data['avatar'])

            bot.send_message(message.chat.id,
                             f'Username: {data["username"]}\n'
                             f'Country: {data["country"][34:]}\n'
                             f'Friends: {data["followers"]}\n'
                             f'{round((time.time() - data["joined"]) / 86_400)}'
                             f' days on Chess.com', reply_markup=markup)

            waiting_for_nick_profile = False

            logger.info('Profile has been sent')

    except Exception:
        bot.send_message(message.chat.id, "Username does not exist. Try again")
        logger.warning('Provided username is not correct')


if __name__ == '__main__':
    logger.info('Started Working')

    # bot.infinity_polling()

    response = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}")
    print(response.json())
    app.run(host='127.0.0.1', port=8444)

    logger.info('Finished Working')

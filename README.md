# Chess-Bot
Bot that can understand user's commands and send the relevant data back by checking up with the official chess.com API.


## Commands: 
- /stats - shows your stats
- /start - shows start message with commands
- /profile - shows your profile info
- /puzzle - shows today's puzzle
- /solve - shows solving moves
- /leaders - shows leaders at categories


## Setup

### Local Development (polling mode)

1. Clone the repository:
   <br>git clone https://github.com/justamanwho/Chess-bot.git
   <br>cd Chess-bot


2. Create and activate virtual environment:
   <br>python -m venv venv
   <br>source venv/bin/activate


3. Install dependencies:
   <br>pip install -r requirements.txt


4. Create a `.env` file with your bot token:
   <br>BOT_NAME=your_telegram_bot_name
   <br>BOT_TOKEN=your_telegram_bot_token


5. In `app.py`, comment out the webhook section and uncomment `bot.infinity_polling()`.


6. Run the bot:
   <br>python app.py

### Production Setup (webhook mode)

1. Clone the repository on your server:
   git clone https://github.com/justamanwho/Chess.git
   <br>cd Chess-bot


2. Create and activate virtual environment:
   <br>python -m venv venv
   <br>source venv/bin/activate


3. Install dependencies:
   <br>pip install -r requirements.txt


4. Create an `.env` file:
   <br>BOT_NAME=your_telegram_bot_name
   <br>BOT_TOKEN=your_telegram_bot_token
   <br>BOT_WEBHOOK=https://yourdomain/chess-webhook


5. Copy the systemd service file from the `setup/` directory:
   <br>sudo cp setup/chess-bot.service /etc/systemd/system/


6. Your server must have a public IP or domain. See `setup/webhook-example.py` for an example webhook endpoint 
   (can be deployed on a portfolio, a website, or any backend).


7. Start and enable the service:
   <br>sudo systemctl daemon-reload
   <br>sudo systemctl start chess-bot.service
   <br>sudo systemctl enable chess-bot.service


8. Check status and logs:
   <br>sudo systemctl status chess-bot.service
   <br>sudo journalctl -u chess-bot.service -f


## Links and Sources:
- telegram bot - https://t.me/chess_info_stats_bot
- chess.com API tutorial - https://youtu.be/KYNbHGs-qG4
- chess module - chess.com   (pip3 install chess.com)
- my nickname - atleastyoutried1 (you can use it to test code)

<img width="388" height="1010" alt="Chess-bot" src="https://github.com/user-attachments/assets/68cef6b1-b6ae-49b1-a2e5-eb6793e3c250" />


## To do list:

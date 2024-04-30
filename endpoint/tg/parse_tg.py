import os
import csv
import json
from datetime import datetime, timedelta
import pytz
import re
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest, GetHistoryRequest
from telethon.tl.types import InputPeerEmpty

def preprocess_message(message):
    # Convert to lowercase
    message = message.lower()

    # Remove links
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    message = url_pattern.sub('', message)

    # Remove specific mention
    message = message.replace('@war_monitor', '')

    # Remove 'upd:'
    message = re.sub(r'upd: ', '', message)

    # Remove symbols
    symbols = '.,;:!•—/()+~→«»-→“”"|#'
    for symbol in symbols:
        message = message.replace(symbol, '')

    # Remove quotes
    message = message.replace('"', '')

    # Remove extra spaces
    message = re.sub(r'\s+', ' ', message.strip())

    # Remove words that begin with '#'
    message = re.sub(r'\b#\w+\b', '', message, flags=re.UNICODE)

    # Replace emojis with spaces
    emoj = re.compile("["
                        u"\U0001F600-\U0001F64F"  # emoticons
                        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                        u"\U0001F680-\U0001F6FF"  # transport & map symbols
                        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                        u"\U00002500-\U00002BEF"  # chinese char
                        u"\U00002702-\U000027B0"
                        u"\U000024C2-\U0001F251"
                        u"\U0001f926-\U0001f937"
                        u"\U00010000-\U0010ffff"
                        u"\u2640-\u2642"
                        u"\u2600-\u2B55"
                        u"\u200d"
                        u"\u23cf"
                        u"\u23e9"
                        u"\u231a"
                        u"\ufe0f"  # dingbats
                        u"\u3030"
                        "]+", re.UNICODE)
    message = re.sub(emoj, ' ', message)

    return message.strip()

def get_messages_today(client, target_chat):
    today_date = datetime.now(pytz.timezone('Europe/Kiev')).date()
    start_date = datetime(today_date.year, today_date.month, today_date.day, 0, 0, 0, tzinfo=pytz.timezone('Europe/Kiev'))
    end_date = datetime(today_date.year, today_date.month, today_date.day, 23, 59, 59, tzinfo=pytz.timezone('Europe/Kiev'))

    all_messages = []
    offset_id = 0
    limit = 100

    while True:
        history = client(GetHistoryRequest(
            peer=target_chat,
            offset_id=offset_id,
            offset_date=end_date.astimezone(pytz.utc).timestamp(),
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        if not history.messages:
            break
        messages = history.messages
        all_messages.extend(messages)
        offset_id = messages[-1].id

    return [(message.date.astimezone(pytz.timezone('Europe/Kiev')).strftime('%H:%M:%S'),
             message.date.astimezone(pytz.timezone('Europe/Kiev')).strftime('%Y-%m-%d'),
             preprocess_message(message.message)) for message in all_messages if start_date <= message.date.astimezone(pytz.timezone('Europe/Kiev')) <= end_date]

def parse_telegram_messages(api_id, api_hash, phone, telegram_password):
    client = TelegramClient(phone, api_id, api_hash)
    client.connect()

    if not client.is_user_authorized():
        try:
            client.start(phone=phone, password=telegram_password)
        except Exception as e:
            print("Error:", e)
            exit()

    chats = client(GetDialogsRequest(
        offset_date=None,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=5,
        hash=0
    )).chats

    target_chat = chats[0] if chats else None

    if not target_chat:
        print("No chats found.")
        exit()

    return client, target_chat

def write_data(data, file_path, format='csv'):
    if format == 'csv':
        with open(file_path, "w", encoding="UTF-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["time", "date", "message"])
            writer.writerows(data)
    elif format == 'json':
        with open(file_path, "w", encoding="UTF-8") as f:
            json.dump(data, f)

def main(api_id, api_hash, phone, telegram_password, folder_path):
    client, target_chat = parse_telegram_messages(api_id, api_hash, phone, telegram_password)
    parsed_data = get_messages_today(client, target_chat)
    file_path_csv = os.path.join(folder_path, "messages_today.csv")
    file_path_json = os.path.join(folder_path, "messages_today.json")
    write_data(parsed_data, file_path_csv, format='csv')
    
    # Save to JSON with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    json_data = {"timestamp": timestamp}  # Only saving the timestamp
    write_data(json_data, file_path_json, format='json')
    
    print(f"Messages saved to CSV: {file_path_csv}")
    print(f"Timestamp saved to JSON: {file_path_json}")


if __name__ == "__main__":
    # Telegram API credentials
    api_id = 123
    api_hash = "---"
    phone = "+---"

    telegram_password = "---"
    # Folder path to save the file
    folder_path = "/---/tg"
    os.makedirs(folder_path, exist_ok=True)
    main(api_id, api_hash, phone, telegram_password, folder_path)

import os
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest, GetHistoryRequest
from telethon.tl.types import InputPeerEmpty
import csv
from datetime import datetime, timedelta
import pytz
from preprocessing_tg import preprocess_message

def parse_telegram_messages(api_id, api_hash, phone, telegram_password):
    # Connect to Telegram client
    client = TelegramClient(phone, api_id, api_hash)
    client.connect()

    # Check if the user is authorized
    if not client.is_user_authorized():
        try:
            client.start(phone=phone, password=telegram_password)
        except Exception as e:
            print("Error:", e)
            exit()

    # Retrieve chats
    chats = []
    last_date = None
    chunk_size = 5
    groups = []
    result = client(GetDialogsRequest(
        offset_date=last_date,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=chunk_size,
        hash=0
    ))
    chats.extend(result.chats)

    # Select the chat with index 0
    if len(chats) > 0:
        target_chat = chats[0]
    else:
        print("No chats found.")
        exit()

    # today's date and time range
    today_date = datetime.now(pytz.timezone('Europe/Kiev')).date()
    start_date = datetime(today_date.year, today_date.month, today_date.day, 0, 0, 0, tzinfo=pytz.timezone('Europe/Kiev'))
    end_date = datetime(today_date.year, today_date.month, today_date.day, 23, 59, 59, tzinfo=pytz.timezone('Europe/Kiev'))

    # Fetch messages
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

    # Clean messages 
    filtered_messages = [(message.date.astimezone(pytz.timezone('Europe/Kiev')).strftime('%H:%M:%S'),
                          message.date.astimezone(pytz.timezone('Europe/Kiev')).strftime('%Y-%m-%d'),
                          preprocess_message(message.message)) for message in all_messages if start_date <= message.date.astimezone(pytz.timezone('Europe/Kiev')) <= end_date]
    
    return filtered_messages

def create_csv_file(data, folder_path):
    # Save 
    file_path = os.path.join(folder_path, "messages_today.csv")
    with open(file_path, "w", encoding="UTF-8") as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        writer.writerow(["time", "date", "message"])
        writer.writerows(data)

    print(f"Messages saved to: {file_path}")

# Telegram API credentials
api_id = 123
api_hash = "-"
phone = "+-"
telegram_password = "-"

# folder path to save the file
folder_path = "/..."  #  folder path
os.makedirs(folder_path, exist_ok=True)  # Create folder if it doesn't exist

# Parse Telegram messages
parsed_data = parse_telegram_messages(api_id, api_hash, phone, telegram_password)

# Create CSV file
create_csv_file(parsed_data, folder_path)

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest, GetHistoryRequest
from telethon.tl.types import InputPeerEmpty
import csv
from datetime import datetime, timedelta
import pytz

api_id = 123
api_hash = "_"
phone = "+_"

client = TelegramClient(phone, api_id, api_hash)

client.start()

chats = []
last_date = None
chunk_size = 200
groups = []
result = client(GetDialogsRequest(
    offset_date=last_date,
    offset_id=0,
    offset_peer=InputPeerEmpty(),
    limit=chunk_size,
    hash=0
))
chats.extend(result.chats)

print("Select a chat for parsing messages:")
for i, chat in enumerate(chats):
    print(f"{i}: {chat.title}")

chat_index = int(input("Enter the chat index: "))
target_chat = chats[chat_index]

start_date = datetime(2022, 2, 24, tzinfo=pytz.timezone('Europe/Kiev'))  # Example: January 1, 2024, in Europe/Kiev timezone 2022-02-24 - 2023-01-25
end_date = datetime(2023, 1, 25, 23, 59, 59, tzinfo=pytz.timezone('Europe/Kiev'))  # Example: January 15, 2024, 23:59:59 in Europe/Kiev timezone

all_messages = []

offset_id = 0
limit = 100

while True:
    history = client(GetHistoryRequest(
        peer=target_chat,
        offset_id=offset_id,
        offset_date=end_date.astimezone(pytz.utc).timestamp(),  # Fetch messages before this timestamp
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

filtered_messages = [msg for msg in all_messages if start_date <= msg.date.astimezone(pytz.timezone('Europe/Kiev')) <= end_date]

with open("messages_period.csv", "w", encoding="UTF-8") as f:
    writer = csv.writer(f, delimiter=",", lineterminator="\n")
    writer.writerow(["time", "date", "message"])
    for message in filtered_messages:
        date = message.date.astimezone(pytz.timezone('Europe/Kiev')).strftime('%Y-%m-%d')
        time = message.date.astimezone(pytz.timezone('Europe/Kiev')).strftime('%H:%M:%S')
        writer.writerow([time, date, message.message])
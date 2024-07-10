from telethon.sync import TelegramClient, events
from telethon.errors import ChatAdminRequiredError, ChannelBannedError, ChannelPrivateError, RPCError, ChatWriteForbiddenError
from telethon import errors
import asyncio
import random
import time
from datetime import datetime, time as dtime, timedelta
import pytz
import os
import sys

# account details (use environment variables for sensitive data)
api_id = os.getenv('API_ID', '20992784')
api_hash = os.getenv('API_HASH', '4732852dfe33392d09804fbafbbf0eae')
phone_number = os.getenv('PHONE_NUMBER', '919872481103')



# bot & owner details 
bot_token = os.getenv('BOT_TOKEN', '7193468978:AAFusqzvq0LfAVL34KX68YZglb8O0M9D4hk')
bot_owner_id = int(os.getenv('BOT_OWNER_ID', '622730585'))

# Add your group IDs here
group_ids = [-1001551429267]

# Dictionary to store minimum and maximum delay times for each group
group_delays = {
    -1001551429267: (7, 14),
}

# Minimum and maximum pause times in seconds
min_pause = 180  # 3 minutes
max_pause = 360  # 6 minutes

# Load messages from messages.txt file
with open('messages.txt', 'r', encoding='utf-8') as file:
    messages = file.read().split('---')

# Clean up messages by stripping whitespace and joining lines correctly
messages = [message.strip().replace('\n', ' \n') for message in messages]

# Define the active time periods in IST (Indian Standard Time)
ist = pytz.timezone('Asia/Kolkata')
active_periods = [
    (dtime(5, 0), dtime(14, 0)),  
    (dtime(16, 0), dtime(23, 59)),  
                 ]

def is_within_active_periods(now):
    for start, end in active_periods:
        if start <= now.time() < end:
            return True
    return False

async def send_messages_to_group(client, group_id, min_delay, max_delay):
    start_time = time.time()
    while True:
        now = datetime.now(ist)
        if is_within_active_periods(now):
            try:
                if time.time() - start_time >= 600:  # 10 minutes in seconds
                    print(f"Script for group {group_id} has run for 10 minutes. Pausing for a while...")
                    await asyncio.sleep(random.randint(min_pause, max_pause))
                    print(f"Resuming script for group {group_id}...")
                    start_time = time.time()

                message = random.choice(messages).strip()
                await client.send_message(group_id, message)
                print(f"Posted in group {group_id}")
                await asyncio.sleep(random.randint(min_delay, max_delay))
            except (ChatAdminRequiredError, ChannelBannedError, ChannelPrivateError, ChatWriteForbiddenError) as e:
                print(f"Skipping group {group_id} due to error: {e}")
                # Remove group from active_group_ids if writing restricted or banned
                if group_id in active_group_ids:
                    active_group_ids.remove(group_id)
                break
            except errors.FloodWaitError as e:
                print(f"Telegram message limitation for group {group_id}. Waiting for {e.seconds} seconds.")
                await asyncio.sleep(e.seconds)
            except RPCError as e:
                print(f"An error occurred in group {group_id}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred in group {group_id}: {e}")
        else:
            next_check = (now + timedelta(minutes=5)).replace(second=0, microsecond=0)
            sleep_seconds = (next_check - now).seconds
            print(f"Current time {now.time()} is outside the active periods. Sleeping for {sleep_seconds} seconds.")
            await asyncio.sleep(sleep_seconds)

async def main():
    client = TelegramClient('session_name', api_id, api_hash)
    bot = TelegramClient('bot', api_id, api_hash)

    await client.start(phone_number)
    await bot.start(bot_token=bot_token)

    # Define active_group_ids to manage dynamically
    global active_group_ids
    active_group_ids = group_ids.copy()

    tasks = []
    for group_id in active_group_ids:
        min_delay, max_delay = group_delays[group_id]
        tasks.append(send_messages_to_group(client, group_id, min_delay, max_delay))

    @bot.on(events.NewMessage(pattern='/restart'))
    async def handler(event):
        if event.sender_id == bot_owner_id:
            await event.respond("Restarting script...")
            print("Restart command received. Restarting script...")
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            await event.respond("You are not authorized to use this command.")

    await asyncio.gather(*tasks, bot.run_until_disconnected())

if __name__ == '__main__':
    asyncio.run(main())
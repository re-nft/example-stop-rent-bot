# This example requires the 'message_content' intent.
import discord
import asyncio

from bot.secrets import get_env_var

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

heartbeat_channel_id = <channel_id> # TODO: input your discord channel id here 
message_queue = asyncio.Queue()
one_minute = 60
one_hour = 60 * one_minute


def add_message_to_notify(msg: str) -> None:
    future = asyncio.run_coroutine_threadsafe(
        message_queue.put(msg),
        client.loop
    )
    future.result()  # Wait for the message to be added to the queue

async def heart_beat():
    while True:
        channel = client.get_channel(heartbeat_channel_id)
        if channel is not None:
            await channel.send("💓 Heartbeat! - polygon collateral free v1")
        await asyncio.sleep(2 * one_hour)  # Sleep for 12 hours

async def notify():
    while True:
        message = await message_queue.get()
        channel = client.get_channel(heartbeat_channel_id)
        if channel is not None:
            await channel.send(message)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    client.loop.create_task(heart_beat())
    client.loop.create_task(notify())

def run_discord_bot():
    client.run(get_env_var('DISCORD_WEBHOOK_TOKEN'))

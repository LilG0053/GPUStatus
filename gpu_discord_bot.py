import discord
from discord.ext import commands
import time
from message_info import DISCORD_TOKEN, TARGET_CHANNEL_ID
class gpu_discord_bot:
    def __init__(self):
        self.alterted_products = {}  # Set to keep track of alerted products
    # Modified send_discord_message function
    async def send_discord_message(self, message, URL=None):
        
        # Intents setup
        intents = discord.Intents.default()
        intents.message_content = True  # Enable message content intent
        print("Sending message attempt")

        self.bot = commands.Bot(command_prefix="!", intents=intents)
        # Send message when bot is ready
        @self.bot.event
        async def on_ready():
            print(f'Logged in as {self.bot.user}')
            try:
                channel = self.bot.get_channel(TARGET_CHANNEL_ID)
                if channel:
                    await channel.send(message)  # Send the message to the channel
                    print(f"Sent message to channel {TARGET_CHANNEL_ID}: {message}")
                else:
                    print(f"Channel with ID {TARGET_CHANNEL_ID} not found.")
            except Exception as e:
                print(f"Error sending message: {e}")
            await self.bot.close()  # Close the bot after sending the message

        # Run the bot
        await self.bot.start(DISCORD_TOKEN)  # This starts the bot asynchronously
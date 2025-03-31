import discord
from discord.ext import commands
from message_info import DISCORD_TOKEN, TARGET_CHANNEL_ID
class gpu_discord_bot:
    # Modified send_discord_message function
    async def send_discord_message(self, message):
        
        
        # Intents setup
        intents = discord.Intents.default()
        intents.message_content = True  # Enable message content intent
        
        # Create bot instance
        bot = commands.Bot(command_prefix="!", intents=intents)
        
        # Send message when bot is ready
        @bot.event
        async def on_ready():
            print(f'Logged in as {bot.user}')
            try:
                channel = bot.get_channel(TARGET_CHANNEL_ID)
                if channel:
                    await channel.send(message)  # Send the message to the channel
                    print(f"Sent message to channel {TARGET_CHANNEL_ID}: {message}")
                else:
                    print(f"Channel with ID {TARGET_CHANNEL_ID} not found.")
            except Exception as e:
                print(f"Error sending message: {e}")
            await bot.close()  # Close the bot after sending the message

        # Run the bot
        await bot.start(DISCORD_TOKEN)  # This starts the bot asynchronously
import os
import discord
from discord.ext import commands
import httpx
from dotenv import load_dotenv
from discord_py_interactions import SlashCommand

load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@slash.slash(name="get_data", description="Fetch data from FastAPI")
async def get_data(ctx):
    async with httpx.AsyncClient() as client:
        response = await client.get('http://localhost:8000/')
        data = response.json()
        await ctx.send(f"Data: {data}")

bot.run(TOKEN)
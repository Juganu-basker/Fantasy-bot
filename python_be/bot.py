import os
import discord
from discord.ext import commands
# import httpx
from dotenv import load_dotenv
from espn_client import ESPNClient


# from discord_py_interactions import SlashCommand
import logging

load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
client = ESPNClient()


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_member_join(member):
    print(f'{member} has joined the server')
    
@bot.event
async def on_member_remove(member):
    print(f'{member} has left the server')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith('!hello'):
        await message.channel.send('Hello!')
    
    if message.content.startswith('!playerStats'):
        await bot.process_commands(message)
    await bot.process_commands(message)


@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.mention}!')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def playerStats(ctx, player_name):
    await ctx.send(f'Player Stats for {player_name}!')
    player_id = client.get_player_id_by_name(player_name)
    if player_id:
        await ctx.send(f'Player ID: {player_id}')
    else:
        await ctx.send(f'Player not found!')
    player_stats = client.get_player_info(player_ids=[player_id])
    if player_stats:
        await ctx.send(f'Player Stats: {player_stats}')
    else:
        await ctx.send(f'Player stats not found!')

    

def run_bot():
    # Configure logging to output to console
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    bot.run(token=TOKEN, log_level=logging.DEBUG)


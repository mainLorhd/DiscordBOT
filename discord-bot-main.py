from config import token
import nacl
import discord
from discord.ext import commands

TOKEN = token
PREFIX = '#'
intents = discord.Intents.all()

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.command()
async def play(ctx, link: str = None):
    if not link:
        await ctx.send("Please write link")
        return

    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("You need to be in a voice channel to use this command.")
        return

    channel = ctx.author.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if voice_client and voice_client.is_connected():
        await ctx.send("I'm already connected to a voice channel!")
    else:
        connected = ctx.author.voice
        await connected.channel.connect()
        await ctx.send(channel)
        await ctx.send("Connected!")

bot.run(TOKEN)

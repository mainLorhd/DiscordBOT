from config import token
import nacl
import discord
from discord.ext import commands
import time

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
        await ctx.send("Connected!")

@bot.command()
async def stop(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client and not voice_client.is_connected():
        await ctx.send("I'm doesn't connected to any Voice Chat")
        return
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()

@bot.event
async def on_voice_state_update(member, before, after):
    voice_client = discord.utils.get(bot.voice_clients, guild=member.guild)
    voice_client = discord.utils.get(bot.voice_clients)
    if len(voice_client.channel.members) == 1:
        time.sleep(10)
        if len(voice_client.channel.members) == 1:
            text_channel = voice_client.guild.system_channel  
            await text_channel.send("I'm alone in Voice Chat for 10 seconds. Bye!")
            await voice_client.disconnect()
            print("I AM LEAVING")
        
            

bot.run(TOKEN)

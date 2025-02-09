from config import token
import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

discord.FFmpegPCMAudio.executable = "C:\\FFMPEG\\bin\\ffmpeg.exe"

TOKEN = token
PREFIX = '#'
intents = discord.Intents.all()

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Настройки для yt-dlp
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # IPv4
}

ffmpeg_options = {
    'options': '-vn',  # Отключаем видео, оставляем только аудио
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@bot.command()
async def play(ctx, url: str = None):
    if not url:
        await ctx.send("Пожалуйста, укажите ссылку на YouTube.")
        return

    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("Вы должны находиться в голосовом канале, чтобы использовать эту команду.")
        return

    channel = ctx.author.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if voice_client and voice_client.is_connected():
        await ctx.send("Я уже подключён к голосовому каналу!")
        return

    # Подключение к голосовому каналу
    try:
        voice_client = await channel.connect()
    except Exception as e:
        await ctx.send(f"Ошибка при подключении: {e}")
        return

    # Воспроизведение аудио
    try:
        player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
        voice_client.play(player, after=lambda e: print('Воспроизведение завершено!'))
        await ctx.send(f"Сейчас играет: **{player.title}**")
    except Exception as e:
        await ctx.send(f"Ошибка при воспроизведении: {e}")
        await voice_client.disconnect()

@bot.command()
async def stop(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client or not voice_client.is_connected():
        await ctx.send("Я не подключён к голосовому каналу.")
        return
    await voice_client.disconnect()
    await ctx.send("Отключился от голосового канала.")

@bot.event
async def on_voice_state_update(member, before, after):
    voice_client = discord.utils.get(bot.voice_clients, guild=member.guild)
    if voice_client and voice_client.is_connected():
        if len(voice_client.channel.members) == 1:  # Если бот один в канале
            await asyncio.sleep(10)  # Ждём 10 секунд
            if len(voice_client.channel.members) == 1:  # Если всё ещё один
                text_channel = voice_client.guild.system_channel
                if text_channel:
                    await text_channel.send("В голосовом канале никого нет уже 10 секунд. Отключаюсь!")
                await voice_client.disconnect()

bot.run(TOKEN)
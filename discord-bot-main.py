from config import token
import discord
from discord.ext import commands
import yt_dlp
import asyncio
from discord import FFmpegPCMAudio

# Устанавливаем путь к FFmpeg
discord.FFmpegPCMAudio.executable = "C:\\FFMPEG\\bin\\ffmpeg.exe"

TOKEN = token
PREFIX = '%'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Опции для yt-dlp (только стриминг, без скачивания)
ydl_opts = {
    'format': 'bestaudio',  # Выбираем лучший аудиоформат
    'quiet': True,          # Отключаем вывод логов
}

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

    # Подключаемся к голосовому каналу, если ещё не подключены
    vc = ctx.voice_client or await channel.connect()

    try:
        # Используем yt-dlp для получения прямой ссылки на аудио
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)  # Получаем информацию о видео без скачивания
            audio_url = info['url']  # Прямая ссылка на аудиопоток
            title = info.get('title', 'Неизвестное название')  # Название трека

        # Воспроизводим аудио через FFmpegPCMAudio
        vc.play(FFmpegPCMAudio(audio_url), after=lambda e: print("Стриминг завершён"))
        await ctx.send(f"Сейчас играет: {title}")

    except Exception as e:
        await ctx.send(f"Произошла ошибка: {str(e)}")

@bot.command()
async def stop(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client or not voice_client.is_connected():
        await ctx.send("Я не подключён к голосовому каналу.")
        return
    await voice_client.disconnect()
    await ctx.send("Отключился от голосового канала.")

@bot.command()
async def pause(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.send("Воспроизведение приостановлено.\n Для возобновления напишите %pause")
        return
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.send("Воспроизведение продолжается.")
        return
        

@bot.event
async def on_voice_state_update(member, before, after):
    voice_client = discord.utils.get(bot.voice_clients, guild=member.guild)
    if voice_client and voice_client.is_connected():
        if len(voice_client.channel.members) == 1:
            await asyncio.sleep(60)
            if len(voice_client.channel.members) == 1:
                text_channel = voice_client.guild.system_channel
                if text_channel:
                    await text_channel.send("В голосовом канале никого нет уже минуту. Отключаюсь!")
                await voice_client.disconnect()

bot.run(TOKEN)
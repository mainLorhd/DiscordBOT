from config import token
import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
from discord import FFmpegPCMAudio
import random

# Устанавливаем путь к FFmpeg
discord.FFmpegPCMAudio.executable = "C:\\FFMPEG\\bin\\ffmpeg.exe"

TOKEN = token
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

# Опции для yt-dlp (только стриминг, без скачивания)
ydl_opts = {
    'format': 'bestaudio',  # Выбираем лучший аудиоформат
    'quiet': True,          # Отключаем вывод логов
}

# Список ответов для команды 8ball
answers = [
    "Это точно.",  # Позитивные
    "Без сомнения.",
    "Несомненно.",
    "Да — определённо.",
    "На это можно положиться.",
    "Как я вижу, да.",
    "Скорее всего.",
    "Перспективы хорошие.",
    "Да.",
    "Знаки указывают на 'да'.",
    "Повтори вопрос позже.",  # Нейтральные
    "Спроси ещё раз попозже.",
    "Сейчас лучше не говорить.",
    "Не могу предсказать сейчас.",
    "Сконцентрируйся и спроси снова.",
    "Не стоит на это рассчитывать.",  # Негативные
    "Мой ответ — нет.",
    "Мои источники говорят 'нет'.",
    "Перспективы не очень хорошие.",
    "Очень сомнительно."
]

# Команда /play
@bot.tree.command(name="play", description="Запускает музыку/видео с YouTube.")
@app_commands.describe(url="Ссылка на YouTube видео")
async def play(interaction: discord.Interaction, url: str):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("Вы должны находиться в голосовом канале, чтобы использовать эту команду.")
        return

    channel = interaction.user.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)

    # Подключаемся к голосовому каналу, если ещё не подключены
    vc = voice_client or await channel.connect()

    try:
        # Используем yt-dlp для получения прямой ссылки на аудио
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)  # Получаем информацию о видео без скачивания
            audio_url = info['url']  # Прямая ссылка на аудиопоток
            title = info.get('title', 'Неизвестное название')  # Название трека

        # Воспроизводим аудио через FFmpegPCMAudio
        vc.play(FFmpegPCMAudio(audio_url), after=lambda e: print("Стриминг завершён"))
        await interaction.response.send_message(f"Сейчас играет: {title}")
    except Exception as e:
        await interaction.response.send_message(f"Произошла ошибка: {str(e)}")

# Команда /stop
@bot.tree.command(name="stop", description="Выключает воспроизведение и отключает бота от канала.")
async def stop(interaction: discord.Interaction):
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if not voice_client or not voice_client.is_connected():
        await interaction.response.send_message("Я не подключён к голосовому каналу.")
        return

    await voice_client.disconnect()
    await interaction.response.send_message("Отключился от голосового канала.")

# Команда /pause
@bot.tree.command(name="pause", description="Ставит воспроизведение на паузу. Возобновляет воспроизведение при повторном использовании команды.")
async def pause(interaction: discord.Interaction):
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await interaction.response.send_message("Воспроизведение приостановлено.\nДля возобновления напишите `/pause`")
        return

    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await interaction.response.send_message("Воспроизведение продолжается.")
        return

# Команда /8ball
@bot.tree.command(name="8ball", description="Спросите у магического шара Шторм.")
@app_commands.describe(question="Ваш вопрос")
async def ball8(interaction: discord.Interaction, question: str):
    embed = discord.Embed(color=7592191)
    embed.add_field(name="🎱Вопрос:", value=question, inline=False)
    embed.add_field(name="🎱Ответ:", value=random.choice(answers), inline=False)
    embed.set_author(name="🎱Магический Шар Шторм🌪")
    await interaction.response.send_message(embed=embed)

# Автоматическое отключение бота, если в канале никого нет
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
@bot.event
async def on_ready():
    try:
        # Очищаем старые команды
        bot.tree.clear_commands(guild=None)
        await bot.tree.sync()
        print(f"Синхронизировано {len(bot.tree.get_commands())} команд.")
    except Exception as e:
        print(f"Ошибка при синхронизации: {e}")
    print(f"Бот {bot.user} запущен!")

# Синхронизация команд при запуске бота
@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        print(f"Синхронизировано {len(bot.tree.get_commands())} команд.")
    except Exception as e:
        print(f"Ошибка при синхронизации: {e}")
    print(f"Бот {bot.user} запущен!")


# Запуск бота
bot.run(TOKEN)
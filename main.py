import asyncio
import concurrent.futures
import os
from discord.ext import commands
import discord
from discord import Intents
from discord import FFmpegPCMAudio
import yt_dlp
import uuid
from config import TOKEN

intents = Intents.all()
client = commands.Bot(command_prefix='+', intents=intents)
executor = concurrent.futures.ThreadPoolExecutor()

queue = []
current_task = None
music_folder = 'music'

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

async def play_next(ctx):
    global queue, current_task
    if queue:
        url = queue.pop(0)
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(music_folder, f'audio_{uuid.uuid4().hex}.%(ext)s'),
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }
            ],
            'keepvideo': False,
        }

        def download_audio():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                audio_file = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            return audio_file

        loop = asyncio.get_running_loop()
        audio_file = await loop.run_in_executor(executor, download_audio)

        def delete_file(error):
            try:
                if os.path.exists(audio_file):
                    os.remove(audio_file)
            except Exception as e:
                print(f"Error deleting file: {e}")
            asyncio.run_coroutine_threadsafe(play_next(ctx), loop)

        vc = ctx.voice_client
        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=audio_file, options='-vn'), after=delete_file)
        await ctx.send(f"Now playing: {url}")
    else:
        current_task = None

@client.command()
async def play(ctx, url: str):
    global current_task
    if not ctx.message.author.voice:
        await ctx.send("You must be in a voice channel to use this command.")
        return

    vc = ctx.voice_client
    if not vc:
        vc = await ctx.message.author.voice.channel.connect()
    
    queue.append(url)
    await ctx.send("Music added to queue.")
    if not current_task:
        current_task = asyncio.create_task(play_next(ctx))

@client.command()
async def add(ctx, url: str):
    global current_task
    queue.append(url)
    await ctx.send("Music added to queue.")
    vc = ctx.voice_client
    if vc and not vc.is_playing() and not vc.is_paused():
        if not current_task:
            current_task = asyncio.create_task(play_next(ctx))

@client.command()
async def stop(ctx):
    global current_task
    vc = ctx.voice_client
    if vc and vc.is_connected():
        vc.stop()
        await vc.disconnect()
        await ctx.send("Disconnected from the voice channel.")
        queue.clear()
        if current_task:
            current_task.cancel()
            current_task = None
    else:
        await ctx.send("I am not connected to a voice channel.")

@client.command()
async def pause(ctx):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await ctx.send("Music paused.")
    else:
        await ctx.send("Music is not playing.")

@client.command()
async def resume(ctx):
    vc = ctx.voice_client
    if vc and vc.is_paused():
        vc.resume()
        await ctx.send("Music resumed.")
    else:
        await ctx.send("Music is already playing.")

@client.command()
async def next(ctx):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.stop()
    await ctx.send("Playing next song.")

client.run(TOKEN)

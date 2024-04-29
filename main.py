import asyncio
import concurrent.futures
import os
from discord.ext import commands
import discord
from discord import Intents
from discord import FFmpegPCMAudio
import yt_dlp
import uuid

intents = Intents.all()
client = commands.Bot(command_prefix='+', intents=intents)
executor = concurrent.futures.ThreadPoolExecutor()

@client.command()
async def play(ctx, url):
    try:
        vc = await ctx.message.author.voice.channel.connect()
        ydl_opts = {
            'format': 'bestaudio/best', 
            'outtmpl': f'audio_{uuid.uuid4().hex}.%(ext)s', 
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }
            ],
            'keepvideo': True,
        }

        await ctx.send("Please wait, starting your music...")

        def download_audio():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                audio_file = ydl.prepare_filename(info_dict)
            return audio_file

        loop = asyncio.get_running_loop()
        audio_file = await loop.run_in_executor(executor, download_audio)

        def delete_file(error):
            os.remove(audio_file)
            
        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=audio_file, options='-vn'), after=delete_file)
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@client.command()
async def stop(ctx):
    vc = ctx.voice_client
    if vc is not None and vc.is_connected():
        vc.stop()
        await vc.disconnect()
        await ctx.send("I have disconnected from the voice channel.")
    else:
        await ctx.send("I am not connected to any voice channel.")

# Creating a playback queue
queue = []

@client.command()
async def pause(ctx):
    vc = ctx.voice_client
    if vc.is_playing():
        vc.pause()
        await ctx.send("Music paused.")
    else:
        await ctx.send("No music is playing.")

@client.command()
async def resume(ctx):
    vc = ctx.voice_client
    if vc.is_paused():
        vc.resume()
        await ctx.send("Music resumed.")
    else:
        await ctx.send("Music is already playing.")

@client.command()
async def add(ctx, url):
    global queue
    queue.append(url)
    await ctx.send("Music added to the queue.")

@client.command()
async def next(ctx):
    global queue
    vc = ctx.voice_client
    if vc is not None and vc.is_connected():
        vc.stop()
    if queue:
        url = queue.pop(0)
        await ctx.send("Now playing the next track.")
    else:
        await ctx.send("The queue is empty.")

client.run('adding your token here')

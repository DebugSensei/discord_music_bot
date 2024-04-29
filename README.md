# discord_music_bot
 - This is a discord bot that lets you listen to music from youtube, how it works: 
# Bot Initialization:
  - intents = Intents.all() allows the bot to use all available Discord API intents to interact with the server.
  - client = commands.Bot(command_prefix='+', intents=intents) creates an instance of the bot with the command prefix +.
# Play Command:
 - Users invoke the +play command with a URL as an argument to play music.
 - The bot connects to the user's voice channel and uses yt_dlp to download audio from YouTube or other supported sites.
 - The downloaded file is converted to an mp3 audio format using FFmpeg.
 - Audio playback is initiated through FFmpegPCMAudio.
 - Once playback is complete, the audio file is deleted.
# Stop Command:
 - Allows users to stop the playback and disconnect the bot from the voice channel.
# Playback Control Commands:
 - +pause pauses the music.
 - +resume resumes playback.
 - +add adds music tracks to the playback queue.
 - +next skips to the next track in the queue.
# Playback Queue:
 - Music tracks can be added to the queue list, which is managed by the add and next commands.
# Bot Launch:
 - client.run('adding your token here') starts the bot using your Discord bot token for authentication.

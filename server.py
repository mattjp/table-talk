import discord
from discord.ext import commands
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

current_sink = None

async def once_done(sink, channel):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("recordings", exist_ok=True)
    
    if sink.audio_data:
        for user_id, audio in sink.audio_data.items():
            filename = f"recordings/user_{user_id}_{timestamp}.mp3"
            with open(filename, 'wb') as f:
                f.write(audio.file.getvalue())
            print(f"Saved recording: {filename}")

@bot.command(name='join')
async def join_voice(ctx):
    global current_sink
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        try:
            voice_client = await channel.connect()
            
            current_sink = discord.sinks.MP3Sink()
            voice_client.start_recording(current_sink, once_done, channel)
            
            await ctx.send(f'Joined {channel.name} and started recording')
        except discord.ClientException:
            await ctx.send('Already connected to a voice channel')
    else:
        await ctx.send('You are not connected to a voice channel')

@bot.command(name='leave')
async def leave_voice(ctx):
    global current_sink
    if ctx.voice_client:
        try:
            if current_sink:
                ctx.voice_client.stop_recording()
                current_sink = None
            
            await ctx.voice_client.disconnect()
            await ctx.send('Stopped recording and disconnected from voice channel')
            
        except Exception as e:
            print(f"Error during leave: {e}")
            try:
                await ctx.voice_client.disconnect()
            except:
                pass
            await ctx.send('Disconnected with error')
    else:
        await ctx.send('Not connected to any voice channel')

if __name__ == '__main__':
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print('Please set DISCORD_BOT_TOKEN environment variable')
        exit(1)
    bot.run(token)
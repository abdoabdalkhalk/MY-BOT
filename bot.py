import discord
from discord.ext import commands, tasks
import os
import asyncio
from flask import Flask
from threading import Thread

# ====== Keep Alive Server ======
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# ====== Bot Settings ======
import os
TOKEN = os.getenv("DISCORD_TOKEN")
TARGET_CHANNEL_ID = 1361055417572004034  # غيره برقم قناتك

replied_messages = set()

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot connected as {bot.user}")
    check_old_messages.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id == TARGET_CHANNEL_ID:
        if message.attachments and message.id not in replied_messages:
            for attachment in message.attachments:
                # بدل الاعتماد على content_type نعتمد على امتداد الصورة
                if attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    await send_thank_you_embed(message)
                    replied_messages.add(message.id)
                    break

    await bot.process_commands(message)

async def send_thank_you_embed(message):
    embed = discord.Embed(
        title="🎉 Thanks for the subscribe!",
        description="Open a ticket to claim your **2 days VIP Basic Panel**.\n\n⚠️ **WARNING:** If this screenshot is not from YouTube, you will get banned from YouTube.",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=message.attachments[0].url)
    embed.set_footer(text="VIP Reward System")
    await message.channel.send(embed=embed)

@tasks.loop(minutes=5)
async def check_old_messages():
    print("🔄 Checking old messages...")
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        print("❌ Channel not found.")
        return

    async for message in channel.history(limit=100):
        if message.id not in replied_messages and message.attachments:
            for attachment in message.attachments:
                if attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    await send_thank_you_embed(message)
                    replied_messages.add(message.id)
                    break

bot.run(TOKEN)

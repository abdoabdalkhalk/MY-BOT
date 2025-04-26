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
TOKEN = os.getenv("TOKEN")
TARGET_CHANNEL_ID = 1365719475982303355

if TOKEN is None or TARGET_CHANNEL_ID is None:
    raise ValueError("❌ Missing TOKEN or TARGET_CHANNEL_ID environment variables.")

replied_messages = set()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

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
                if attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    await send_thank_you_embed(message)
                    replied_messages.add(message.id)
                    break

    await bot.process_commands(message)

async def send_thank_you_embed(message):
    embed = discord.Embed(
        title="🎉 Thanks for subscribing!",
        description=(
            "Open a ticket to claim your **1-day VIP Basic Panel**.\n\n"
            "[Click here to open a ticket 🎟️](https://discord.com/channels/1319471351047786590/1319475322743164929)\n\n"
            "⚠️ **WARNING:** If this screenshot is not from YouTube, you will be banned from the server."
        ),
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=message.attachments[0].url)
    embed.set_footer(text="VIP Reward System")
    await message.reply(embed=embed)  # <==== هنا بدل send إلى reply مباشرة على الرسالة

@tasks.loop(minutes=5)
async def check_old_messages():
    print("🔄 Checking old messages...")
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not isinstance(channel, discord.TextChannel):
        print("❌ Target channel is not a TextChannel.")
        return

    async for message in channel.history(limit=100):
        if message.id not in replied_messages and message.attachments:
            for attachment in message.attachments:
                if attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    await send_thank_you_embed(message)
                    replied_messages.add(message.id)
                    break

bot.run(TOKEN)

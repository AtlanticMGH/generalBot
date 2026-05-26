yimport discord
import os
import dotenv
import time
import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

dotenv.load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

client = discord.Bot(intents=intents, max_messages=5000)

cogs_list = [
    "adminBasis",
    "generellBasis",
]
for cog in cogs_list:
    client.load_extension(f"cogs.{cog}")

def start_timer():
    """Startet den Timer."""
    global start_time
    start_time = time.time()

def get_runtime():
    """Gibt die Laufzeit des Bots in Sekunden zurück."""
    global start_time
    if start_time is None:
        return 0
    current_time = time.time()
    runtime = current_time - start_time
    return round(runtime, 2)

start_timer()

@client.event
async def on_ready():
    for guild in client.guilds:
        print(f"- {guild.name}")

@client.command(description="Pingt den Bot")
async def ping(ctx):
    try:
        rounded_latency = round(client.latency * 1000)  # Latenz in ms
        embed = discord.Embed(
            title="Bot Status",
            color=discord.Color.green(),
            description=f"""**Der bot ist Online**
Ping: **{rounded_latency}ms**
Online: **{get_runtime()}** Sekunden"""
        )
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"Fehler beim Test-Kommando: {str(e)}")
        await ctx.send("Ein Fehler ist aufgetreten!", ephemeral=True)

@client.command(description="Test Befehl")
async def test(ctx):
    try:
        embed = discord.Embed(title="Test",
                      colour=0x14ec1a)

        await ctx.respond(embed=embed, ephemeral=True)
    except Exception as e:
        print(f"Fehler aufgetreten: {e}")
    #await ctx.respond("Test", ephemeral=True)

client.run(str(os.getenv("TOKEN")))

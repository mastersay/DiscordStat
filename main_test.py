import random

from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
import discord

client = commands.Bot(command_prefix="/")
slash = SlashCommand(client, sync_commands=True)


@client.event
async def on_ready():
    print("online")
@client.command()
async def this(ctx):
    await ctx.send("ide")

options = [
    {
        'name': "start",
        'description': "A",
        'required': False,
        'type': 4
    },
    {
        'name': "stop",
        'description': "B",
        'required': False,
        'type': 4
    },
]


@slash.slash(name='guess', description="guess number", guild_ids=[764941750229270539])
async def _guess(ctx: SlashContext):
    await ctx.send(content=f"random: {random.randint(1, 2)}")


client.run("")

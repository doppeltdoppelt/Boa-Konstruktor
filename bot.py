import discord
from discord.ext import commands
from dislash import InteractionClient
from utilcog import UtilCog
from musiccog import MusicCog

bot = commands.Bot(command_prefix='/', intents=discord.Intents.default())
slash = InteractionClient(bot, test_guilds=[887285894577528852])

bot.add_cog(UtilCog(slash))
bot.add_cog(MusicCog(slash))

with open("token.txt") as file:
    bot.run(file.read())

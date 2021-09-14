from discord.ext import commands

from maincog import MainCog
from musikcog import MusikCog

bot = commands.Bot(command_prefix='/')
bot.remove_command('help')

bot.add_cog(MainCog(bot))
bot.add_cog(MusikCog(bot))

token = ""
with open("token.txt") as file:
    token = file.read()

bot.run(token)

import discord
import nacl
from discord.ext import commands


class MainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.helpMessage = """
```
General commands:
/help - Zeigt diese Nachricht

Musik commands:
/p <keywords> - Spielt nen Song (derzeit nur Youtube).
/q - Zeigt die Queue an.
/skip - Skippt.
```
"""

        await self.send_to_all(self.helpMessage)

    @commands.command(name="help", help="Displays all the available commands")
    async def help(self, ctx):
        await ctx.send(self.helpMessage)

    @commands.command()
    async def leave(ctx):
        if ctx.guild.voice_client.is_connected():  # Checking that they're in a vc
            await ctx.guild.voice_client.disconnect()
        else:
            await ctx.send("Sorry, I'm not connected to a voice channel at the moment.")

    @commands.command()
    async def join(ctx):
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()  # This will error if the bot doesn't have sufficient permissions
        else:
            await ctx.send("You're not connected to a channel at the moment.")

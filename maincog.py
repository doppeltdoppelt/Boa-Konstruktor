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

    @commands.command(name="help", help="Displays all the available commands")
    async def help(self, ctx):
        await ctx.send(self.helpMessage)

    @commands.command()
    async def leave(self, ctx):
        if ctx.guild.voice_client.is_connected():  # VC check
            await ctx.guild.voice_client.disconnect()
        else:
            await ctx.send("Ich bin grad nirgendwo verbunden.")

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()  # Errort bei unzureichenden Permissions
        else:
            await ctx.send("Du bist grad nirgendwo verbunden.")

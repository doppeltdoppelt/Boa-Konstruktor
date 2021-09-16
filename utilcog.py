import discord
from discord.ext import commands
from dislash import slash_command

util_str_dict = {'help_desc': "Zeigt die verfügbaren Commands und deren Argumente in einer Nachricht an",
                     'leave_desc': "Leaved den zu dem derzeitig verbundenen Voice-Channel",
                     'join_desc': "Joint dem Voice-Channel des Befehlsausführers.",
                     
                     'leave_sucs_msg': f"Erfolgreich aus dem derzeitigen Voice-Channel geleaved.\nID: ",
                     'leave_fail_msg': "Ich bin nirgendwo verbunden (oder der Bot wurde neugestartet. Kick mich)!",
                     'join_sucs_msg': f"Erfolgreich deinem Voice-Channel gejoined.\nID: ",
                     'join_fail_msg_usr': "Du bist nirgendwo verbunden!",
                     'join_fail_msg_perms': "Ich habe nicht die erforderlichen Permissions!",
                     'help_msg': """
General commands:
/help - Zeigt diese Nachricht

Musik commands:
/play <keywords> - Spielt nen Song (derzeit nur Youtube).
/queue - Zeigt die Queue an.
/skip - Skippt.
"""
                     }


class UtilCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="help", description=util_str_dict['help_desc'])
    async def help(self, inter):
        embed = discord.Embed(title='Hilfe-Nachricht',
                              description=util_str_dict['help_msg'],
                              color=0x789c48)
        await inter.send(embed=embed)

    @slash_command(name="leave", description=util_str_dict['leave_desc'])
    async def leave(self, inter):
        try:
            await inter.guild.voice_client.disconnect()
            channel = discord.utils.get(inter.guild.voice_channels, name=str(inter.author.voice.channel))
            embed = discord.Embed(title='Erfolg!',
                                  description=util_str_dict['leave_sucs_msg'] + str(channel.id),
                                  color=0x789c48)
            await inter.send(embed=embed)
        except AttributeError:
            embed = discord.Embed(title='Fehlschlag!',
                                  description=util_str_dict['leave_fail_msg'],
                                  color=0xea131b)
            await inter.send(embed=embed)

    @slash_command(name="join", description=util_str_dict['join_desc'])
    async def join(self, inter):
        try:
            await inter.author.voice.channel.connect()
            channel = discord.utils.get(inter.guild.voice_channels, name=str(inter.author.voice.channel))
            embed = discord.Embed(title='Erfolg!',
                                  description=util_str_dict['join_sucs_msg'] + str(channel.id),
                                  color=0x789c48)
            await inter.send(embed=embed)
        except AttributeError:
            embed = discord.Embed(title='Fehlschlag!',
                                  description=util_str_dict['join_fail_msg_usr'],
                                  color=0xea131b)
            await inter.send(embed=embed)
        except Exception:
            embed = discord.Embed(title='Fehlschlag!',
                                  description=util_str_dict['join_fail_msg_perms'],
                                  color=0xea131b)
            await inter.send(embed=embed)

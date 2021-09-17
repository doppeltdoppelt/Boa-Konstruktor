import discord
from discord.ext import commands
from dislash import slash_command, Option, OptionType
from youtube_dl import YoutubeDL

music_str_dict = {'p_desc': 'Sucht nach einem bestimmten Suchbegriff oder URL und spielt diese ab.',
                  'q_desc': 'Zeigt die derzeitig ausstehende Queue an abzuspielenden Songs an.',
                  'skip_desc': 'Skippt den derzeitig spielenden Song.',

                  'p_fail_msg_type': 'Konnte den Song nicht downloaden.',
                  'p_play_msg': 'Now playing: ',
                  'p_add_msg': 'Zur Queue hinzugefuegt:',
                  'p_fail_msg_usr': 'Connecte erstmal!',
                  'q_fail_msg_noval': 'Keine anstehenden Titel gefunden!',
                  'skip_sucs_msg': 'Erfolgreich geskippt:',
                  'skip_fail_msg_noval': 'Kein Song mehr, der geskippt werden koennte!'
                  }


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'False'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}

        self.channel_con_to = ""
        self.currently_playing = ""
        self.is_playing = False

    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception:
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    async def play_next(self, inter):
        if len(self.music_queue) > 0:
            self.is_playing = True

            self.currently_playing = self.music_queue[0][0]['title']
            m_url = self.music_queue[0][0]['source']
            embed = discord.Embed(title=music_str_dict['p_play_msg'],
                                  description=str(self.music_queue[0][0]['title']),
                                  color=0x789c48)
            await inter.send(embed=embed)
            self.music_queue.pop(0)
            self.channel_con_to.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(inter))

        else:
            self.is_playing = False
            await inter.voice_client.disconnect()

    async def play_music(self, inter):
        if len(self.music_queue) > 0:
            self.is_playing = True

            self.currently_playing = self.music_queue[0][0]['title']
            m_url = self.music_queue[0][0]['source']

            embed = discord.Embed(title=music_str_dict['p_play_msg'],
                                  description=str(self.music_queue[0][0]['title']),
                                  color=0x789c48)
            await inter.send(embed=embed)

            if self.channel_con_to == "" or not self.channel_con_to.is_connected() or self.channel_con_to is None:
                self.channel_con_to = await self.music_queue[0][1].connect()
            else:
                await self.channel_con_to.move_to(self.music_queue[0][1])

            self.music_queue.pop(0)
            try:
                await self.channel_con_to.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(inter))
            except TypeError:
                print("TODO: FIX THIS ALREADY")

        else:
            self.is_playing = False

    @slash_command(name="play",
                   description=music_str_dict['p_desc'],
                   options=[Option('suchbegriff', 'Wort, Satz oder URL', OptionType.STRING, required=True)]
                   )
    async def p(self, inter, suchbegriff):
        try:
            song = self.search_yt(suchbegriff)
            if type(song) == type(True):
                await inter.send(music_str_dict['p_fail_msg_type'])
            else:
                self.music_queue.append([song, inter.author.voice.channel])

                if self.is_playing:
                    embed = discord.Embed(title=music_str_dict['p_add_msg'],
                                          description=str(self.music_queue[-1][0]['title']),
                                          color=0x789c48)
                    await inter.send(embed=embed)

                else:
                    await self.play_music(inter)

        except AttributeError:
            await inter.send(music_str_dict['p_fail_msg_usr'])

    @slash_command(name="queue", description=music_str_dict['q_desc'])
    async def q(self, inter):
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += f"{str(i)}. {self.music_queue[i][0]['title']}\n"

        if retval != "":
            embed = discord.Embed(title='Auslesung der Queue:',
                                  description=retval,
                                  color=0x789c48)
            await inter.send(embed=embed)

        else:
            embed = discord.Embed(title='Auslesung der Queue:',
                                  description=music_str_dict['q_fail_msg_noval'],
                                  color=0x789c48)
            await inter.send(embed=embed)

    @slash_command(name="skip", description=music_str_dict['skip_desc'])
    async def skip(self, inter):
        if self.channel_con_to != "":
            print(self.currently_playing)
            embed = discord.Embed(title='Erfolg!',
                                  description=music_str_dict['skip_sucs_msg'] + self.currently_playing,
                                  color=0x789c48)
            await inter.send(embed=embed)
            self.channel_con_to.stop()
        await self.play_music(inter)

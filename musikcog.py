import discord
import nacl
from discord.ext import commands

from youtube_dl import YoutubeDL


class MusikCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.isPlaying = False  # bot soll nicht abspielen wenn er schon abspielt

        # array mit [song, channel]
        self.musikQueue = []
        self.YDL_OPTIONS = {'formats': 'bestaudio', 'noplaylist': 'True'}
        self.FFMEPG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}

        self.vChannel = ""  # stored den derzeitigen voice channel, etwas gescuffed aber funktioniert

    def search_youtube(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ytdl:
            try:
                info = ytdl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception:  # lmao
                return False
        return {'source': info['formats'][0]['url'], 'title': info['title']}  # dictionary fuer die songinfos

    def next_song(self):
        # wir koennen keine playlist abspielen die leer ist
        if len(self.musikQueue) > 0:
            self.isPlaying = True

            url = self.musikQueue[0][0]['source']  # erste URL aus dem dictionary kriege n
            self.musikQueue.pop(0)  # erstes Element loeschen, da mans ja grade spielt

            self.vChannel.play(discord.FFmpegPCMAudio(url, **self.FFMEPG_OPTIONS), after=lambda e: self.next_song)
        else:
            self.isPlaying = False

    async def play_song(self):
        if len(self.musikQueue) > 0:
            self.isPlaying = True

            url = self.musikQueue[0][0]['source']

            # try connect zum voicechannel, falls noch nicht, oder move wenn schon falsch connected
            if self.vChannel == "" or self.vChannel is None or not self.vChannel.is_connected():
                self.vChannel = await self.musikQueue[0][1].connect()
            else:
                await self.vChannel.move_to(self.musikQueue[0][1])

            print(self.musikQueue)

            self.musikQueue.pop(0)

            self.vChannel.play(discord.FFmpegPCMAudio(url, **self.FFMEPG_OPTIONS), after=lambda e: self.next_song)
        else:
            self.isPlaying = False

    # main start
    @commands.command(name="play", help="Spielt nen Song (derzeit nur Youtube).")
    async def p(self, ctx, *args):
        query = " ".join(args)

        authorv_channel = ctx.author.voice.channel
        if authorv_channel is None:
            await ctx.send("Du musst zu einem Voice Channel connected sein, damit der bot weiss, wo er hinsoll!")
        else:
            song = self.search_youtube(query)
            if type(song) == type(True):  # loesung scuffed as shit, aber hatte den bug bei lofi livestreams
                await ctx.send(
                    "Konnte den Song nicht hinzufuegen. Sogar der Entwickler weiss nicht, warum. Vermeidet Livestreams.")
            else:
                await ctx.send("Song zur Queue hinzugefuegt.")
                self.musikQueue.append([song, authorv_channel])

                if not self.isPlaying:
                    await self.play_song()

    # playlist anzeigen
    @commands.command(name="queue", help="Zeigt die Queue an.")
    async def q(self, ctx):
        retval = ""
        for i in range(0, len(self.musikQueue)):
            # title anzeigen
            retval += self.musikQueue[i][0]['title'] + "\n"

        print(retval)
        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("Keine Musik in der Queue.")

    # skip
    @commands.command(name="skip", help="Skippt.")
    async def skip(self, ctx):
        if self.vChannel != "" and self.vChannel:
            self.vChannel.stop()
            await self.play_song()

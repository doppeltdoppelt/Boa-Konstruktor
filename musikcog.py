import discord
import random
from discord.ext import commands

from youtube_dl import YoutubeDL

show_currently_playing = True


class MusikCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # conciousness = True

        self.isPlaying = False  # bot soll nicht abspielen wenn er schon abspielt

        # array mit [song, channel]
        self.musikQueue = []
        self.YDL_OPTIONS = {'formats': 'bestaudio', 'noplaylist': 'True'}
        self.FFMEPG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}

        self.vChannel = ""  # stored den derzeitigen voice channel, etwas gescuffed aber funktioniert

    async def search_youtube(self, item, ctx, check):
        if check:
            ctx.send("Request angekommen! Suche nach " + item)

        with YoutubeDL(self.YDL_OPTIONS) as ytdl:
            try:
                info = ytdl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception:  # lmao
                return False
        if check:
            ctx.send("Habe das hier gefunden: " + info['title'])
        print({'source': info['formats'][0]['url'], 'title': info['title']})
        return {'source': info['formats'][0]['url'], 'title': info['title']}  # dictionary fuer die songinfos

    async def next_song(self, ctx):
        # wir koennen keine playlist abspielen die leer ist
        if len(self.musikQueue) > 0:
            self.isPlaying = True
            if show_currently_playing:
                await ctx.send("Playing now: " + self.musikQueue[0][0]['title'])
            url = self.musikQueue[0][0]['source']  # erste URL aus dem dictionary kriegen
            self.musikQueue.pop(0)  # erstes Element loeschen, da mans ja grade spielt

            self.vChannel.play(discord.FFmpegPCMAudio(url, **self.FFMEPG_OPTIONS), after=lambda e: self.next_song(ctx))
        else:
            self.isPlaying = False

    async def play_song(self, ctx):
        if len(self.musikQueue) > 0:
            self.isPlaying = True

            url = self.musikQueue[0][0]['source']
            if show_currently_playing:
                await ctx.send("Playing now: " + self.musikQueue[0][0]['title'])
            # try connect zum voicechannel, falls noch nicht, oder move wenn schon falsch connected
            if self.vChannel == "" or self.vChannel is None or not self.vChannel.is_connected():
                self.vChannel = await self.musikQueue[0][1].connect()
            else:
                await self.vChannel.move_to(self.musikQueue[0][1])

            self.musikQueue.pop(0)

            self.vChannel.play(discord.FFmpegPCMAudio(url, **self.FFMEPG_OPTIONS), after=lambda e: self.next_song(ctx))
        else:
            self.isPlaying = False

    # main start
    @commands.command(name="play", help="Spielt nen Song (derzeit nur Youtube).")
    async def play(self, ctx, *args):
        query = " ".join(args)

        authorv_channel = ctx.author.voice.channel
        if authorv_channel is None:
            await ctx.send("Du musst zu einem Voice Channel connected sein, damit der bot weiss, wo er hinsoll!")
        else:
            song = self.search_youtube(query, ctx, True)
            if type(song) == type(True):  # loesung scuffed as shit, aber hatte den bug bei lofi livestreams
                await ctx.send(
                    "Konnte den Song nicht hinzufuegen. Vermeidet Livestreams for now, ich kuemmer mich drum.")
            else:
                await ctx.send("Playing now: " + self.musikQueue[0][0]['title'])
                self.musikQueue.append([song, authorv_channel])

                if not self.isPlaying:
                    await self.play_song(ctx)

    # playlist anzeigen
    @commands.command(name="queue", help="Zeigt die Queue an.")
    async def queue(self, ctx):
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
            await self.play_song(ctx)

    @commands.command(name="shuffle", help="Shuffled die derzeitige Queue.")
    async def shuffle(self, ctx):
        random.shuffle(self.musikQueue)
        await ctx.send("Playlist geshuffled!")
        return self.musikQueue

    @commands.command(name="stop", help="Hoert auf, Musik zu spielen und verlaesst den Channel.")
    async def stop(self, ctx):
        await ctx.voice_client.disconnect()
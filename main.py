import discord
from discord.ext import commands
from Discord_chatbot.Data_Control_Files.Steam_API import *
from Discord_chatbot.Data_Control_Files.Twitch_API import *


class stitchBot(commands.Bot):

    def __init__(self, prefix):
        commands.Bot.__init__(self, command_prefix=prefix)
        self.client = discord.Client()
        self.online = "[StitchBot] Online!"
        self.command_set()
        self.event_set()
        self.channel_list = []
        self.last_message = ''

    async def on_ready(self):
        print(self.online)
        self.channels_to_list()
        channel = self.channel_list[0]
        await channel.send("**✅ [StitchBot] Online!**")

    def channels_to_list(self):
        print('started')
        for guild in bot.guilds:
            for channel in guild.text_channels:
                self.channel_list.append(channel)
                print(self.channel_list)

    def event_set(self):

        @self.event
        async def on_member_join(member):
            print(f'**{member} has joined the server.**')

        @self.event
        async def on_member_remove(member):
            print(f'**{member} has left the server.**')

        @self.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.errors.CommandNotFound or Exception):
                await ctx.send('**Invalid command used**')

    def command_set(self):

        @self.command()
        async def hello(ctx):
            await ctx.channel.send('**Hello** :yum:')

        @self.command()
        async def clear(ctx, amount=5):
            await ctx.channel.purge(limit=amount)

        @self.command()
        async def kick(ctx, target: discord.member):
            if target.server_permissions.administrator:
                await bot.say("**Target is an admin**")

            else:
                try:
                    await ctx.kick(target)
                    await ctx.say(f'**Kicked:{target}**')
                except Exception as e:
                    await bot.say(f'''**Something went wrong:**
```{e}```''')

        @self.command()
        async def ban(ctx, member: discord.member, *, reason=None):
            await member.ban(reason=reason)

        @self.command()
        async def unban(ctx, *, member):
            banned_user = await ctx.guild.bans()
            member_name, member_discriminator = member.split('#')

            for ban_entry in banned_user:
                user = ban_entry.user

                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    await ctx.guild.unban(user)
                    await ctx.send(f'**unbanned {user.mention}**')
                    return

        @self.command()
        async def stream(ctx):
            await ctx.send('**Enter Streamers name**')

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            streamers_name = await bot.wait_for('message', check=check)

            try:
                print('searching')
                streamers_id = twitchHandler.getStreamerID(streamers_name.content)
                print(streamers_id)
                stream_checker = twitchHandler.checkIfStreaming(streamers_id)
                if not stream_checker:
                    await ctx.channel.send(f'''
**:white_circle:{streamers_name.content}**
**They are not live right now**:sob:
''')
                else:
                    details = twitchHandler.streamDetails(streamers_id)

                    def live_emoji():
                        if details['type'] == 'live':
                            return ':red_circle:'
                        else:
                            return ''
                    live = live_emoji()

                    await ctx.channel.send(f'''
**{live+details['user_name']}** 
```diff
- {details['type']}
+ Title: {details['title']}
+ Viewers: {details['viewer_count']}
+ Started at: {details['started_at']}
+ Language: {details['language']}
```''')

            except Exception as i:
                print('failed to find', i)
                await ctx.channel.send('**Streamer not found**')

        @self.command()
        async def game(ctx):
            await ctx.send('**Enter game name**')

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            game_name = await bot.wait_for('message', check=check)

            try:
                print('searching')
                game_id = steam_APIM.findGameID(game_name.content)
                player_count = steam_APIM.gamePlayerCount(game_id)
                await ctx.channel.send(f'** - {game_name.content}** \n **Player Count: {player_count}**')

            except Exception as i:
                print('failed to find', i)
                await ctx.channel.send('**Game not found**')

        @self.command()
        async def commands(ctx):
            await ctx.send("""
**- Commands:**
```diff
- !hello 
- !clear
- !kick
- !ban
- !unban
- !game
- !commands
```""")

        @self.command()
        async def info(ctx):
            await ctx.send('''

''')


if __name__ == '__main__':
    bot = stitchBot(prefix='!')
    # bot.run('Nzc1Mzg0NTE2NzUxMTMwNjI0.X6ljGg.Gapcl2lnc_pqNuvTuZ3l2MNOtYI')
    bot.run('NzcxNzM2MzExMjI0NDY3NDU3.X5wdcg.rTamw-fIcHyNdXMalAEMgsufDFU')

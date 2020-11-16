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
                await ctx.say("**Target is an admin**")

            else:
                try:
                    await ctx.kick(target)
                    await ctx.say(f'**Kicked:{target}**')
                except Exception as e:
                    await ctx.say(f'''**Something went wrong:**
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
                    await ctx.channel.send(f'**unbanned {user.mention}**')
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
                    vod = twitchHandler.latestStreamerClips(streamers_id)

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
+ Top Clip of stream:
```
{vod}
''')

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
                steamHandler.storeGameList()
                print('searching')
                game_id = steamHandler.findGameID(game_name.content)
                player_count = steamHandler.gamePlayerCount(game_id)
                game_desc = steamHandler.gameDescription(game_id)
                game_cost = steamHandler.getGamePrice(game_id)

                if game_cost['free']:
                    game_cost = 'Free'

                elif float(game_cost['normal_price'][1:]) > float(game_cost['current_price'][1:]):
                    current_price = game_cost['current_price']
                    print()
                    money_saved = (float(game_cost['normal_price'][1:]) - float(game_cost['current_price'][1:]))

                    game_cost = f'''Sale Price:{current_price}
+ {game_cost['normal_price'][0]}{"%.2f" % money_saved} Off!'''
                else:
                    current_price = game_cost['current_price']
                    game_cost = f'Game Price: {current_price}'

                await ctx.channel.send(f'''** - {game_name.content}**
```diff
+ {game_cost}
+ Player Count: {player_count}
+ Game Description:\n {game_desc}
```''')

            except Exception as i:
                print('failed to find', i)
                await ctx.channel.send('**Game not found**')

        @self.command()
        async def stats(ctx):

            await ctx.channel.send('**Enter Steam URL**')

            try:
                def check(msg):
                    return msg.author == ctx.author and msg.channel == ctx.channel

                steam_url = await bot.wait_for('message', check=check)
                steam_id = steamHandler.getUserSteamID(steam_url.content)
                csgo_stats = steamHandler.getCSGOStats(steam_id)

                if not csgo_stats:
                    await ctx.channel.send('**Couldn`t find stats**')

                else:
                    await ctx.channel.send(f''':first_place:** - CSGO Stats**
```diff
+ Total Kills: {csgo_stats['total_kills']}
+ Total Headshots: {csgo_stats['total_kills_headshot']}
+ Total Damage: {csgo_stats['total_damage_done']}
+ Total Deaths: {csgo_stats['total_deaths']}
+ Total Wins: {csgo_stats['total_wins']}
+ Total PlayTime in Match {int(csgo_stats['total_time_played'])//3600}hrs 
```''')

            except Exception as e:
                await ctx.channel.send(f'**Error Fetching Stats,**\n```{e}```')

        @self.command()
        async def commands(ctx):
            await ctx.send("""
**- Commands:**
```diff
- !info
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
:information_source:**Info**
```diff
+ This is Stitch Bot ,It is an interactive Discord Bot that helps Gamers gain information about the games they love and the Streamers they watch. It can help you find the most popular game to play and tell you when your favourite streamer is Streaming. It can also help with your usual basic commands like Kick and Ban. Use !commands to see the full capabilities of Stitch Bot. 
```''')


if __name__ == '__main__':
    bot = stitchBot(prefix='!')
    bot.run('')

# imports:
import discord
import sys
from discord.ext import commands
from discord.ext.commands import has_permissions, check
from discord import Embed, Color
from Discord_chatbot.Data_Control_Files.Steam_API import *
from Discord_chatbot.Data_Control_Files.Twitch_API import *
from Discord_chatbot.Data_Control_Files.Local_Store import storageHandler
import asyncio
from Encryption import encryptionAES128
from Bot_response import response_proccessing

"""This is Stitch Bots Main source code. Stitch Bot is an interactive discord bot that gives information about streamers 
and games that you want to know about, it also stores users preferences and keeps you updated on the latest games and 
streamers that you want to track"""

"""
comment structure:
{Method Short Description}
{Input Arguments and their types}
{Output Details}
{Exception Details}
"""


class DM_access:
    def __init__(self):
        self.access_dict = {}
        self.dm_list = []

    def access(self, id, name):

        storageHandler.checkIfChecked(id,name)


# Stitch Bot main class
class stitchBot(commands.Bot):

    def __init__(self, prefix):
        """
        initialising methods, attributes and objects that are needed, these include:
        - Object:
            commands.Bot - part of the discord library used to create commands
        - Functions:
            command&event_set - starts all events and commands the bot has set
        - attributes:
            guild_dict - dictionary of all the servers(and channels in that server) the Bot is in
            channel_list = list of all the text channels the Bot can send to
        """
        commands.Bot.__init__(self, command_prefix=prefix)
        self.command_set()
        self.event_set()
        self.loop.create_task(self.background_tracker())
        self.guild_dict = {}
        self.channel_list = []
        self.embed = Embed
        self.colour = Color(0x000000)
    # METHODS THAT ARE NOT COMMANDS OR EVENTS:

    # - on_ready function - part of discord.py function starts when bot is ready
    async def on_ready(self):
        self.channels_to_list()
        for guild in self.guilds:
            embed = discord.Embed(
                title=f'✅**Online!**',
                description='Stitch Bot is online',
                colour=self.colour)
            embed.set_image(url='https://media.giphy.com/media/AsMOCCJf9b9dVsRh63/giphy.gif')

            # sends online text and a gif to the servers first text channel

            await guild.text_channels[0].send(embed=embed)

    # - adds servers and channels to the guild_dict and adds channels to the channel list
    def channels_to_list(self):
        print('started')
        for guild in self.guilds:
            for channel in guild.text_channels:
                if not isinstance(channel, discord.channel.DMChannel):

                    self.channel_list.append(channel)
                    print(self.channel_list)
            self.guild_dict[guild] = self.channel_list

    @staticmethod
    def correct_channel(ctx):
        if not ctx.channel.name == 'questions':
            return True

    async def background_tracker(self):
        await self.wait_until_ready()
        while not self.is_closed():
            print('running')
            for user in storageHandler.trackedStreamList():
                id = user[0]
                print(id)
                streamer = user[1]
                for name in streamer:
                    if not storageHandler.checkIfChecked(await self.fetch_user(int(id)), name):
                        streamers_id = twitchHandler.getStreamerID(name)
                        print(streamers_id)
                        stream_checker = twitchHandler.checkIfStreaming(streamers_id)
                        print(stream_checker)
                        if not stream_checker:
                            pass
                        else:
                            details = twitchHandler.streamDetails(streamers_id)
                            print(details)
                            vod = twitchHandler.latestStreamerClips(streamers_id)

                            if not vod:
                                vod = ''

                            clip = '+ Popular clip from the stream:'
                            title = f"**{details['user_name']}**"
                            desc = f'''- {details['type']}
                                            - Title: {details['title']}
                                            - Viewers: {details['viewer_count']}
                                            - Started at: {details['started_at']}
                                            - Language: {details['language']}
                                            {clip}'''

                            embed = discord.Embed(
                                title=f'{title}',
                                description=f'{desc}',
                                colour=self.colour, )
                            user_dm = await self.fetch_user(int(id))
                            print(user_dm)
                            await user_dm.send(embed=embed)
                            await user_dm.send(vod)
            await asyncio.sleep(1800)



    '''
    - sets all events for discord bots
    Events Include:
        - on_member_join
        - on_member_remove
        - on_command_error
    '''
    def event_set(self):

        # - EVENTS (@self.event decorator used to show discord.py that these methods are events)

        @self.event
        async def on_member_join(member):
            print(f'**{member} has joined the server.**')

        @self.event
        async def on_member_remove(member):
            print(f'**{member} has left the server.**')

        # - Error handling:
            # - if a command is spelt wrong or does not exist it will send invalid command

        @self.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.errors.CommandNotFound or Exception):
                await ctx.send('**Invalid command used**')
            else:
                await ctx.send(f'**Error occured:**\n```{error}```')

        @self.event
        async def on_message(message):
            print(message)
            if isinstance(message.channel, discord.channel.TextChannel):
                if message.channel.name == 'questions':
                    if not message.content == '':
                        if not message.author.id == bot.user.id:
                            await message.channel.send(f'**{response_proccessing(message.content, message.author)}**')

            await bot.process_commands(message)

    '''
    - Sets all commands for discord Bot
    These Include:
        - !hello
        - !clear
        - !kick
        - !ban
        - unban
        - !stream
        - !game
        - !stats
        - !command
    '''
    def command_set(self):
        # - COMMANDS (@self.command decorator)

        @self.command()
        @check(self.correct_channel)
        async def hello(ctx):
            await ctx.channel.send('**Hello** :yum:')

        '''
        clears conversation by x amount of lines 
        parameters:
            ctx - context object that discord.py passes in when command is invoked
            amount - the amount of lines that you want to be cleared
        '''
        @self.command()
        @check(self.correct_channel)
        async def clear(ctx, amount=5):
            await ctx.channel.purge(limit=amount)

        '''
        kicks user specified from the discord server that the command was invoked in
         parameters:
            ctx - line 121
            member - type:(abc.Snowflake)The member to kick from their server.
            reason - reason for user to be kicked, always set to None 
        Note: Two decorators to make sure correct permissions are required
        '''
        @self.command()
        @check(self.correct_channel)
        @has_permissions(kick_members=True)
        async def kick(ctx, member: discord.Member, *, reason=None):
            await member.kick(reason=reason)
            await ctx.send(f'**User {member} has been kicked**')
        '''
        Same as Kick command but for Banning(see line 128)
        '''
        @self.command()
        @check(self.correct_channel)
        @has_permissions(ban_members=True)
        async def ban(ctx, member: discord.Member, *, reason=None):
            await member.ban(reason=reason)
            await ctx.send(f'**User {member} has been banned**')
        '''
        Unbans User specified from server that command was invoked
        parameters:
            see kick command 
        '''
        @self.command()
        @check(self.correct_channel)
        async def unban(ctx):
            banned_user = await ctx.guild.bans()
            banned_user_list = []
            itterate = 0

            for ban_entry in banned_user:
                user = ban_entry.user
                banned_user_list.append(f'{itterate} -{user.name}')
                itterate = itterate+1
            title = '**Banned Users:**'
            desc = '\n'.join(banned_user_list)+'\n**Enter number of user you want to unban**'

            embed = discord.Embed(
                title=f'{title}',
                description=f'{desc}',
                colour=self.colour, )

            await ctx.send(embed=embed)

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            user_unban = await bot.wait_for('message', check=check)

            if user_unban.content.isnumeric():
                await ctx.guild.unban(banned_user[int(user_unban.content)].user)
                await ctx.channel.send(f'**unbanned {banned_user[int(user_unban.content)].user}**')
            else:
                await ctx.channel.send('**Incorrect Number**')

        @self.command()
        async def test(ctx):
            print(await ctx.guild.bans())

        @self.command()
        @check(self.correct_channel)
        async def stream(ctx):
            await ctx.send('**Enter Streamers name**')

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            streamers_name = await bot.wait_for('message', check=check)

            print('searching')
            streamers_id = twitchHandler.getStreamerID(streamers_name.content)

            if not streamers_id:
                raise Exception('Streamer not Found')

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
                if not vod:
                    clip = ''
                    vod = ''
                else:
                    clip = '+ Popular clip from the stream:'

                def live_emoji():
                    if details['type'] == 'live':
                        return ':red_circle:'
                    else:
                        return ''
                live = live_emoji()

                title = f"**{live+details['user_name']}**"
                desc = f'''- {details['type']}
                - Title: {details['title']}
                - Viewers: {details['viewer_count']}
                - Started at: {details['started_at']}
                - Language: {details['language']}
                {clip}'''

                embed = discord.Embed(
                    title=f'{title}',
                    description=f'{desc}',
                    colour=self.colour, )

                await ctx.send(embed=embed)

                if not vod == '':
                    await ctx.send(vod)

        @self.command()
        @check(self.correct_channel)
        async def game(ctx):
            await ctx.send('**Enter game name**')

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            game_name = await bot.wait_for('message', check=check)

            print('searching')
            game_id = steamHandler.findGameID(game_name.content)
            if not game_id:
                raise Exception('Game not found')

            def game_price_calc(id):
                price_dict = steamHandler.getGamePrice(id)
                if price_dict['free']:
                     normal_price = 0
                     current_price = 0
                     money_saved = 0
                     sale = False
                elif price_dict['normal_price'] == '':
                    normal_price = 0
                    current_price = price_dict['current_price']
                    money_saved = 0
                    sale = False
                else:
                    current_price = price_dict['current_price']
                    normal_price = price_dict['normal_price']
                    sale = True
                    x = float(price_dict['normal_price'][1:])
                    y = float(price_dict['current_price'][1:])
                    z = price_dict['current_price'][:1]
                    money_saved = f'{z}{x-y}'
                return normal_price, current_price, money_saved, sale

            normal_price, current_price, money_saved, sale = game_price_calc(game_id)

            if normal_price == 0 and current_price == 0 and money_saved == 0:
                game_cost = 'Free'
            elif sale:
                game_cost = f'Sale Price: {current_price}\n{money_saved} Off!'
            else:
                game_cost = f'Price: {current_price}'
            player_count = steamHandler.gamePlayerCount(game_id)
            game_desc = steamHandler.gameDescription(game_id)
            game_trailer = steamHandler.getGameTrailers(game_id)
            title = f'** - {game_name.content}**'
            desc = (f'''- {game_cost}
                    - Player Count: {player_count}
                    - Game Description:\n {game_desc}
                    - Trailer:''')

            embed = discord.Embed(
                title=f'{title}',
                description=f'{desc}',
                colour=self.colour, )

            await ctx.send(embed=embed)
            await ctx.send(game_trailer)

        @self.command()
        @check(self.correct_channel)
        async def stats(ctx):
            await ctx.channel.send('**Enter Steam URL**')

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel
            steam_url = await bot.wait_for('message', check=check)
            print(steam_url.content)
            steam_id = steamHandler.getUserSteamID(steam_url.content)
            csgo_stats = steamHandler.getCSGOStats(steam_id)
            if not csgo_stats:
                desc = '**Couldn`t find stats**'
            else:
                if type(csgo_stats['total_time_played']) == bool:
                    hours = 'unknown'
                else:
                    hours = int(csgo_stats['total_time_played'])//3600
                desc = (f'''+ Total Kills: {csgo_stats['total_kills']}
                - Total Headshots: {csgo_stats['total_kills_headshot']}
                - Total Damage: {csgo_stats['total_damage_done']}
                - Total Deaths: {csgo_stats['total_deaths']}
                - Total Wins: {csgo_stats['total_wins']}
                - Total PlayTime in Match {hours}hrs 
                ''')

            title = ':first_place:** - CSGO Stats**'

            embed = self.embed(
                title=f'{title}',
                description=f'{desc}',
                colour=self.colour, )

            await ctx.send(embed=embed)

        @self.command()
        @check(self.correct_channel)
        async def commands(ctx):
            title = '- Commands:'
            desc = """
            - !hello
            - !clear
            - !kick
            - !ban
            - unban
            - !stream
            - !game
            - !stats
            - !command
            """
            embed = self.embed(
                title=f'{title}',
                description=f'{desc}',
                colour=self.colour, )

            await ctx.send(embed=embed)

        @self.command()
        @check(self.correct_channel)
        async def info(ctx):
            title = ':information_source:**Info**'
            desc = '''This is Stitch Bot ,It is an interactive Discord Bot that helps Gamers gain information about 
            the games they love and the Streamers they watch. It can help you find the most popular game to play 
            and tell you when your favourite streamer is Streaming. It can also help with your usual basic 
            commands like Kick and Ban. Use !commands to see the full capabilities of Stitch Bot. '''

            embed = self.embed(
                title=f'{title}',
                description=f'{desc}',
                colour=self.colour)
            embed.set_image(url='https://i.ibb.co/zRDVL3B/Stitch-Bot-logo.jpg')

            await ctx.send(embed=embed)

        @self.group()
        async def pref(ctx):
            if ctx.invoked_subcommand is None:
                title = '**Preferences 🖥️**'
                desc = '''**1** - favourite_streamers
                        **2** - favourite_games
                        **3** - favourite_genres
                        **4** - tracked_game
                        **5** - tracked_stream
                        **6** - blacklisted_streamers
                        
                        - Or use **pref remove** for removing preferences'''

                embed = self.embed(
                    title=title,
                    description=desc,
                    colour=self.colour
                )
                await ctx.send(embed=embed)

        @pref.command(name='1')
        async def favourite_streamers(ctx):
            await ctx.send('**Enter your favourite streamer** (you can have up to 10)')

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            favourite_streamers = await bot.wait_for('message', check=check)

            def check_real_streamer(streamer):
                if not twitchHandler.getStreamerID(streamer):
                    return False
                else:
                    return True
            if check_real_streamer(favourite_streamers.content):
                storageHandler.writeUserDetails(favourite_streamers.author.id, "favourite_streamers", f"{favourite_streamers.content}")
                await ctx.send('**+ Preference Added**')

            else:
                await ctx.send('**Streamer Not Found**')

        @pref.command(name='2')
        async def favourite_games(ctx):
            await ctx.send('**Enter your favourite Games** (you can have up to 10)')

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            favourite_games = await bot.wait_for('message', check=check)

            def favourite_games_check(games):
                if not steamHandler.findGameID(games):
                    return False
                else:
                    return True

            if favourite_games_check(favourite_games.content):
                storageHandler.writeUserDetails(favourite_games.author.id, "favourite_games", f"{favourite_games.content}")
                await ctx.send('**+ Preference Added**')
            else:
                await ctx.send('**Game Not Found**')

        @pref.command(name='3')
        async def favourite_genres(ctx):
            await ctx.send('**Enter your favourite Genre** (you can have up to 10)')

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            favourite_genre = await bot.wait_for('message', check=check)
            if len(favourite_genre.content) < 30:
                storageHandler.writeUserDetails(favourite_genre.author.id, "favourite_games",
                                                f"{favourite_genre.content}")
                await ctx.send('**+ Preference Added**')
            else:
                await ctx.send('**Genre name too large**')

        @pref.command(name='4')
        async def tracked_game(ctx):
            await ctx.send('**Enter the game you want to Track** (you can have up to 10)')

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            tracked_games = await bot.wait_for('message', check=check)

            def tracked_games_check(games):
                if not steamHandler.findGameID(games):
                    return False
                else:
                    return True

            if tracked_games_check(tracked_games.content):
                storageHandler.writeUserDetails(tracked_games.author.id, "tracked_game",
                                                f"{tracked_games.content}")
                await ctx.send('**+ Preference Added**')
            else:
                await ctx.send('**Game Not Found**')

        @pref.command(name='5')
        async def tracked_stream(ctx):
            await ctx.send('**Enter a Streamer you want to track** (you can have up to 10)')

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            tracked_streamers = await bot.wait_for('message', check=check)

            def check_real_streamer(streamer):
                if not twitchHandler.getStreamerID(streamer):
                    return False
                else:
                    return True

            if check_real_streamer(tracked_streamers.content):
                storageHandler.writeUserDetails(tracked_streamers.author.id, "tracked_streamer",
                                                f"{tracked_streamers.content}")
                await ctx.send('**+ Preference Added**')

            else:
                await ctx.send('**Streamer Not Found**')

        @pref.command(name='6')
        async def blacklisted_streamers(ctx):
            await ctx.send('**Enter the streamer you want to Blacklist** (you can have up to 10)')

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            blacklisted_streamer = await bot.wait_for('message', check=check)

            def check_real_streamer(streamer):
                if not twitchHandler.getStreamerID(streamer):
                    return False
                else:
                    return True

            if check_real_streamer(blacklisted_streamer.content):
                storageHandler.writeUserDetails(blacklisted_streamer.author.id, "blacklisted_streamers",
                                                f"{blacklisted_streamer.content}")
                await ctx.send('**+ Preference Added**')

            else:
                await ctx.send('**Streamer Not Found**')

        @pref.command()
        async def remove(ctx):
            title = '**Remove Preferences 🖥️**'
            desc = 'enter the number corresponding to the data you want to remove'
            details = storageHandler.readUserDetailsDict(ctx.author.id)
            if not details:
                await ctx.send('**No preferences stored for that user**')

            count = 1
            stuffs = []
            for iter, item in enumerate(details.values()):
                if not item == '':
                    if not iter == 0:
                        if item is not None:
                                if type(item) == list:
                                    for stuff in item:
                                        desc += f'\n**{count}** - {stuff}'
                                        count += 1
                                        stuffs.append(stuff)
                                else:
                                    desc += f'\n**{count}** - {stuff}'
                                    count += 1
                                    stuffs.append(stuff)
            embed = self.embed(
                title=title,
                description=desc,
                colour=self.colour
            )
            await ctx.send(embed=embed)
            await ctx.send('**Enter number corresponding to the item you wish to remove**')

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            item_to_remove = stuffs[int((await bot.wait_for('message', check=check)).content)-1]

            def get_key(value):
                keys = details.keys()
                for key in keys:
                    if type(details.get(key)) == list:
                        for item in details.get(key):
                            if item == value:
                                return key
                    if details.get(key) == value:
                        return key

            storageHandler.deleteUserDetails(ctx.author.id, get_key(item_to_remove), item_to_remove)
            await ctx.send('** - Preference removed**')


if __name__ == '__main__':
    filePath = os.path.dirname(__file__)

    # setting decrypt key
    decrypt_key_path = os.path.join(filePath, "Discord_chatbot\Data_Control_Files\Encrypted_keys\Decrypt_key")
    with open(decrypt_key_path, 'r') as decrypt_key_file:
        decrypt_key = decrypt_key_file.read()
    encryption = encryptionAES128(decrypt_key)

    # Acquiring encrypted discord token from text file

    discord_key_path = os.path.join(filePath, "Discord_chatbot\Data_Control_Files\Encrypted_keys\Discord_key.txt")
    with open(discord_key_path, 'rb') as key_file:
        encrypted_token = key_file.read()
    token = encryption.decrypt(encrypted_token)

    bot = stitchBot(prefix='!')
    bot.run(f'{token}')

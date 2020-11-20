# imports:
import discord
import sys, os
from discord.ext import commands
from discord.ext.commands import has_permissions
# from Discord_chatbot.Data_Control_Files.Steam_API import *
# from Discord_chatbot.Data_Control_Files.Twitch_API import *
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

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
        self.discord = discord.Client()
        self.command_set()
        self.event_set()
        self.guild_dict = {}
        self.channel_list = []

    # METHODS THAT ARE NOT COMMANDS OR EVENTS:

    # - on_ready function - part of discord.py function starts when bot is ready
    async def on_ready(self):
        self.channels_to_list()
        for guild in self.guilds:
            # gif
            path = os.path.dirname(__file__)
            gif_path = "../Discord-Bot/images/Stitch.gif"
            final_gif_path = os.path.join(path, gif_path)
            file = discord.File(final_gif_path)

            # sends online text and a gif to the servers first text channel

            await guild.text_channels[0].send('✅**Online!**')
            await guild.text_channels[0].send(file=file)

    # - adds servers and channels to the guild_dict and adds channels to the channel list
    def channels_to_list(self):
        print('started')
        for guild in self.guilds:
            for channel in guild.text_channels:
                self.channel_list.append(channel)
                print(self.channel_list)
            self.guild_dict[guild] = self.channel_list

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

        # - COMMANDS

        @self.command()
        async def hello(ctx):
            await ctx.channel.send('**Hello** :yum:')

        '''
        clears conversation by x amount of lines 
        parameters:
            ctx - context object that discord.py passes in when command is invoked
            amount - the amount of lines that you want to be cleared
        '''
        @self.command()
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
        @has_permissions(kick_members=True)
        async def kick(ctx, member: discord.Member, *, reason=None):
            await member.kick(reason=reason)
            await ctx.send(f'**User {member} has been kicked**')
        '''
        Same as Kick command but for Banning(see line 128)
        '''
        @self.command()
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
        async def unban(ctx, *, member: discord.Member):
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
                print('Error Occurred:', i)
                await ctx.channel.send(f'**{i}**')

        @self.command()
        async def game(ctx):
            await ctx.send('**Enter game name**')

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            game_name = await bot.wait_for('message', check=check)

            try:
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

                await ctx.channel.send(f'''** - {game_name.content}**
```diff
+ {game_cost}
+ Player Count: {player_count}
+ Game Description:\n {game_desc}
+ Trailer:
```
{game_trailer}''')

            except Exception as i:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print('Error Occurred:', i)
                await ctx.channel.send(f'**{i}**')

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


class encryptionAES128:

    def __init__(self, key):
        self.connected = False
        self.BLOCK_SIZE = 16
        self.KEY = self.hash(key)
        self.CIPHER = AES.new(self.KEY, AES.MODE_ECB)
        self.password = ''

    def encrypt(self, data):
        encrypted = self.CIPHER.encrypt(bytes(self.pad(data)))
        return encrypted

    def decrypt(self, data):
        decrypted = self.CIPHER.decrypt(data)
        msg = self.depad(decrypted.decode())
        return msg

    def pad(self, data):
        if (len(data) % self.BLOCK_SIZE) != 0:
            data = data + (self.BLOCK_SIZE - (len(data) % self.BLOCK_SIZE)) * '~'
            return data.encode()
        else:
            return data

    @staticmethod
    def depad(data):
        padsize = data.count('~')
        raw_data = data[:len(data) - padsize]
        return raw_data

    def hash(self, data):
        hashing = SHA256.new(bytes(data.encode()))
        return hashing.digest()


if __name__ == '__main__':
    # x = encryption.encrypt('Nzc1Mzg0NTE2NzUxMTMwNjI0.X6ljGg.QLQfSL9RKk9t31tNooMQWXyMbe4')
    # print(x)
    encrypted_token = b'\xd0\xa0\x85i"\xa2a\x0e\x9b\xad\x18\xbe\x86\xce\xfeA\x85l\xa9\xf4T<\xdeF\xf0 \xdd\xc6\x13c_E\xcd\x9dn5\xa72r\xa2x\xe8-\xcb\'\xd2Z\xa9\xc3\xae\xf3w\xa7\x1f\x08\xe0\xc7\xc2\x0e\xcc\xfd<G\xf2'
    decrypt_key = input('Enter Decrypt Key:')
    encryption = encryptionAES128(f'{decrypt_key}')
    token = encryption.decrypt(encrypted_token)
    bot = stitchBot(prefix='!')
    bot.run(f'{token}')
import discord
from discord.ext import commands
from Discord_chatbot.Data_Control_Files.Steam_API import *


class stitchBot(commands.Bot):

    def __init__(self, prefix):
        commands.Bot.__init__(self, command_prefix=prefix)
        self.client = discord.Client()
        self.online = "[StitchBot] Online!"
        self.command_set()
        self.channel_list = []

    async def on_ready(self):
        print(self.online)

    async def on_connect(self):
        self.channels_to_list()
        channel = self.channel_list[0]
        await channel.send("**✅ [StitchBot] Online!**")

    def channels_to_list(self):
        print('started')
        for guild in bot.guilds:
            for channel in guild.text_channels:
                self.channel_list.append(channel)
                print(self.channel_list)

    def command_set(self):

        @self.command(name='GameInfo', pass_context=True)
        async def game_info(ctx):
            await ctx.send('**Enter game name**')

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            game_name = await bot.wait_for("message", check=check)
            try:
                print('searching')
                game_id = steam_APIM.findGameID(game_name)
                await ctx.channel.send(game_id)

            except Exception as i:
                print('failed to find', i)
                await ctx.channel.send('**Game not found**')


if __name__ == '__main__':
    bot = stitchBot(prefix='!')
    bot.run()

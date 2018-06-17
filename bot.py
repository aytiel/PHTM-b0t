import discord
from discord.ext import commands

import settings.config

extensions = ['cogs.arcdps', 'cogs.control']

class PHTMb0t(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=settings.config.PREFIX, case_insensitive=True)
        
        self.status_format = '{} days since the last raid release'
        
        for ext in extensions:
            try:
                self.load_extension(ext)
            except Exception as e:
                exc = '{}: {}'.format(type(e).__name__, e)
                print('Failed to load extension {}\n{}'.format(ext, exc))

    async def on_ready(self):
        print('Logged in...')
        print('Username: ' + str(bot.user.name))
        print('Client ID: ' + str(bot.user.id))
        invite = 'https://discordapp.com/oauth2/authorize?&client_id=' + str(bot.user.id) + '&scope=bot&permissions=0'
        print('Invite URL: ' + invite)
        status = discord.Game(name='DPS Simulator 2018')
        await bot.change_presence(activity=status)

    async def on_message(self, message):
        if not message.author.bot:
            await bot.process_commands(message)

bot = PHTMb0t()
bot.run(settings.config.TOKEN)
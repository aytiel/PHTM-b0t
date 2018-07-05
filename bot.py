import datetime

import discord
from discord.ext import commands

import settings.config

extensions = ['cogs.arcdps', 'cogs.control']

class PHTMb0t(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=settings.config.PREFIX, case_insensitive=True)
        
        self.status_format = '{} days without a new raid wing'
        
        for ext in extensions:
            try:
                self.load_extension(ext)
            except Exception as e:
                exc = '{}: {}'.format(type(e).__name__, e)
                print('Failed to load extension {}\n{}'.format(ext, exc))

    async def on_ready(self):
        print('Logged in...')
        print('Username: ' + str(self.user.name))
        print('Client ID: ' + str(self.user.id))
        invite = 'https://discordapp.com/oauth2/authorize?&client_id=' + str(self.user.id) + '&scope=bot&permissions=0'
        print('Invite URL: ' + invite)
        await self.update_status()

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)
            
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if ctx.command.qualified_name == 'login':
                await ctx.send('One or more required parameters are missing. Please execute the command as follows:\n`{}login [username][password]`'.format(settings.config.PREFIX))
            elif ctx.command.qualified_name == 'upload':
                await ctx.send('One or more required parameters are missing. Please execute the command as follows:\n`{}upload [raids/fractals][title]`'.format(settings.config.PREFIX))
            else:
                await ctx.send('ERROR :robot:')
            
    async def update_status(self):
        diff = datetime.date.today() - datetime.date(2017, 11, 28)
        status = discord.Game(name=self.status_format.format(diff.days))
        await self.change_presence(activity=status)

bot = PHTMb0t()
bot.run(settings.config.TOKEN)
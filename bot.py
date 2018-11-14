import json
import datetime
import traceback
import sys

import discord
from discord.ext import commands

import settings.config
import settings.version

extensions = ['cogs.arcdps', 'cogs.control']

class PHTMb0t(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=settings.config.PREFIX, case_insensitive=True)
        
        self.status_format = 'Current User: {}'
        self.emoji_list = []
        self.clear_list = []
        with open('cogs/data/logs.json', 'r') as user_file:
            user = json.load(user_file)
        self.owner_name = user['user']['name']
        self.owner_id = user['user']['id']
        self.owner_key = user['user']['key']
        self.owner_filepath = user['user']['filepath']
        
        self.remove_command('help')
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
        invite = 'https://discordapp.com/api/oauth2/authorize?client_id={}&permissions=27648&scope=bot'.format(str(self.user.id))
        print('Invite URL: ' + invite)
        
        await self.update_status(self.owner_name)
        for emoji in self.emojis:
            if emoji.guild.id == 457052141920583680:
                self.emoji_list.append(emoji)
        
        print('------------------------------')
        print('GW2 LOG BOT v{}'.format(settings.version.VERSION))
        print('------------------------------')
        print('CHANGE LOG:\n{}'.format(settings.version.CHANGE_LOG))

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)
            
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
            
        error = getattr(error, 'original', error)
        
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.UserInputError):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            if ctx.command.qualified_name == 'login':
                await ctx.send('One or more required parameters are missing. Please execute the command as follows:\n`{}login [username] [password]`'.format(settings.config.PREFIX))
            elif ctx.command.qualified_name == 'upload':
                await ctx.send('One or more required parameters are missing. Please execute the command as follows:\n`{}upload [raids/fractals] [title]`'.format(settings.config.PREFIX))
            else:
                await ctx.send('ERROR :robot:')
                
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            
    async def update_status(self, name: str):
        self.owner_name = name
        status = discord.Game(name=self.status_format.format(name))
        await self.change_presence(activity=status)

bot = PHTMb0t()
bot.run(settings.config.TOKEN)
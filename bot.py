import json
import datetime

import discord
from discord.ext import commands

import settings.config

extensions = ['cogs.arcdps', 'cogs.control']

class PHTMb0t(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=settings.config.PREFIX, case_insensitive=True)
        
        self.status_format = 'Current User: {}'
        with open('cogs/data/logs.json', 'r') as user_file:
            user = json.load(user_file)
        self.owner_name = user['user']['name']
        self.owner_id = user['user']['id']
        self.owner_key = user['user']['key']
        
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
        invite = 'https://discordapp.com/oauth2/authorize?&client_id={}&scope=bot&permissions=0'.format(str(self.user.id))
        print('Invite URL: ' + invite)
        await self.update_status(self.owner_name, self.owner_id, self.owner_key)

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)
            
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if ctx.command.qualified_name == 'login':
                await ctx.send('One or more required parameters are missing. Please execute the command as follows:\n`{}login [username] [password]`'.format(settings.config.PREFIX))
            elif ctx.command.qualified_name == 'upload':
                await ctx.send('One or more required parameters are missing. Please execute the command as follows:\n`{}upload [raids/fractals] ["title"]`'.format(settings.config.PREFIX))
            else:
                await ctx.send('ERROR :robot:')
            
    async def update_status(self, name: str, id: int, key: str):
        self.owner_name = name
        self.owner_id = id
        self.owner_key = key
        status = discord.Game(name=self.status_format.format(name))
        await self.change_presence(activity=status)

bot = PHTMb0t()
bot.run(settings.config.TOKEN)
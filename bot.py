import discord
from discord.ext import commands

import settings.config

bot = commands.Bot(command_prefix=settings.config.PREFIX)

@bot.event
async def on_ready():
    print('Logged in...')
    print('Username: ' + str(bot.user.name))
    print('Client ID: ' + str(bot.user.id))
    print('Invite URL: ' + 'https://discordapp.com/oauth2/authorize?&client_id=' + bot.user.id + '&scope=bot&permissions=0')
    
@commands.command()
async def ping():
    await bot.say('Pong!')

@commands.command()
async def shutdown():    
    await bot.logout()
    await bot.close()

bot.add_command(ping)
bot.add_command(shutdown)    
bot.run(settings.config.TOKEN)
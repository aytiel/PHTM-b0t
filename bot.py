import discord
from discord.ext import commands

import settings.config

bot = commands.Bot(command_prefix=settings.config.PREFIX)
extensions = ['cogs.arcdps']

@bot.event
async def on_ready():
    print('Logged in...')
    print('Username: ' + str(bot.user.name))
    print('Client ID: ' + str(bot.user.id))
    status = discord.Game(name='DPS Simulator 2018')
    await bot.change_presence(activity=status)

@bot.event
async def on_message(message):
    if not message.author.bot:
        await bot.process_commands(message)
    
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def shutdown(ctx):
    guild = ctx.guild
    if guild is None:
        has_perms = False
    else:
        has_perms = ctx.channel.permissions_for(guild.me).manage_messages
    if has_perms:
        await ctx.message.delete()
    else:
        await ctx.send('I do not have permissions to delete messages. Please enable this in the future.')
    await bot.logout()
    await bot.close()

for ext in extensions:
    bot.load_extension(ext)
bot.run(settings.config.TOKEN)
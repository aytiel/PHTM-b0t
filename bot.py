import datetime
import json
import requests

import asyncio
import discord
from discord.ext import commands

import settings.config

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in...')
    print('Username: ' + str(client.user.name))
    print('Client ID: ' + str(client.user.id))
    print('Invite URL: ' + 'https://discordapp.com/oauth2/authorize?&client_id=' + client.user.id + '&scope=bot&permissions=0')
    
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith(settings.config.PREFIX):
        message.content = message.content[1:].lower()
        
    if message.content.startswith('ping'):
        msg = 'Pong!'
        await client.send_message(message.channel, msg)
    
client.run(settings.config.TOKEN)
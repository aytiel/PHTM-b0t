# https://github.com/Rapptz/discord.py/blob/async/examples/reply.py
import discord

TOKEN = 'NDU3MDUzMDQ0NjMxMTQyNDAx.DgTfkA.ADDu79ZtpPjALZMi9V1Vh6YyfJw'

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)

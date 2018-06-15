import json
import requests
import datetime

import discord
from discord.ext import commands

class Arcdps:
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def test(self, ctx):
        await ctx.send('The cog works!')
        
def setup(bot):
    bot.add_cog(Arcdps(bot))
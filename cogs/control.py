import discord
from discord.ext import commands

class Control:
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong!')

    @commands.command()
    async def shutdown(self, ctx):
        guild = ctx.guild
        if guild is None:
            has_perms = False
        else:
            has_perms = ctx.channel.permissions_for(guild.me).manage_messages
        if has_perms:
            await ctx.message.delete()
        else:
            await ctx.send('I do not have permissions to delete messages. Please enable this in the future.')
        await self.bot.logout()
        await self.bot.close()
        
def setup(bot):
    bot.add_cog(Control(bot))
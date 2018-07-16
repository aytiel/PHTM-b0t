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
            
        if self.bot.owner_id == 0 or not self.bot.owner_id == ctx.author.id:
            return await ctx.send('You do not have permission to use the bot currently. Only the current user may use the bot.')    
            
        await self.bot.logout()
        await self.bot.close()
        
def setup(bot):
    bot.add_cog(Control(bot))
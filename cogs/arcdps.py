import json
import requests
import datetime
import glob
import os

import discord
from discord.ext import commands

raid_logs = {
    'W1': {
        'Vale Guardian': None,
        'Gorseval the Multifarious': None,
        'Sabetha the Saboteur': None
    },
    'W2': {
        'Slothasor': None,
        'Matthias Gabrel': None
    },
    'W3': {
        'Keep Construct': None,
        'Xera': None
    },
    'W4': {
        'Cairn the Indomitable': None,
        'Mursaat Overseer': None,
        'Samarog': None,
        'Deimos': None
    },
    'W5': {
        'Soulless Horror': None,
        'Dhuum': None
    }
}

frac_logs = {
    '99CM': {
        'MAMA': None,
        'Nightmare Oratuss': None,
        'Ensolyss of the Endless Torment': None
    },
    '100CM': {
        'Skorvald the Shattered': None,
        'Artsariiv': None,
        'Arkk': None
    }
}

class Arcdps:
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def upload(self, ctx, type: str, name: str):
        guild = ctx.guild
        if guild is None:
            has_perms = False
        else:
            has_perms = ctx.channel.permissions_for(guild.me).manage_messages
        if has_perms:
            await ctx.message.delete()
        else:
            await ctx.send('I do not have permissions to delete messages. Please enable this in the future.')
            
        if not type == 'raids' and not type == 'fractals':
            await ctx.send('Please indicate whether you want to upload **raids** or **fractals** logs.')
            return
            
        date = '`' + str(datetime.date.today()) + '`'
        await ctx.send(date)
        title = '__' + name + '__'
        await ctx.send(title)
        
        if type == 'raids':
            for w in raid_logs:
                wing = w + ':'
                await ctx.send(wing)
                for b in raid_logs[w]:
                    path = 'C:/Users/atl/Documents/Guild Wars 2/addons/arcdps/arcdps.cbtlogs/' + b + '/*'
                    all_files = glob.glob(path)
                    latest_file = max(all_files, key=os.path.getctime)
                    if latest_file is None:
                        raid_logs[w][b] = None
                        
                    dps_endpoint = 'https://dps.report/uploadContent?json=1&rotation_weap1=0&generator=rh'
                    files = {'file': open(latest_file, 'rb')}
                    res = requests.post(dps_endpoint, files=files)
                    if not res.status_code == 200:
                        raid_logs[w][b] = None
                    else:
                        raid_logs[w][b] = json.loads(res.text)
                    
                    if raid_logs[w][b] is None:
                        await ctx.send('ERROR 🤖')
                    else:
                        await ctx.send(raid_logs[w][b]['permalink'])
        else:
            for s in frac_logs:
                scale = s + ':'
                await ctx.send(scale)
                for b in frac_logs[s]:
                    path = 'C:/Users/atl/Documents/Guild Wars 2/addons/arcdps/arcdps.cbtlogs/' + b + '/*'
                    all_files = glob.glob(path)
                    latest_file = max(all_files, key=os.path.getctime)
                    if latest_file is None:
                        frac_logs[s][b] = None
                        
                    dps_endpoint = 'https://dps.report/uploadContent?json=1&rotation_weap1=0&generator=rh'
                    files = {'file': open(latest_file, 'rb')}
                    res = requests.post(dps_endpoint, files=files)
                    if not res.status_code == 200:
                        frac_logs[s][b] = None
                    else:
                        frac_logs[s][b] = json.loads(res.text)
                    
                    if frac_logs[s][b] is None:
                        await ctx.send('ERROR 🤖')
                    else:
                        await ctx.send(frac_logs[s][b]['permalink'])
        
def setup(bot):
    bot.add_cog(Arcdps(bot))
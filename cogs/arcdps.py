import json
import requests
import datetime
import glob
import os

import discord
from discord.ext import commands
import settings.config

logs = {
    'raids': {
        'W1': {
            'Vale Guardian': {'dps.report': None, 'GW2Raidar': None},
            'Gorseval the Multifarious': {'dps.report': None, 'GW2Raidar': None},
            'Sabetha the Saboteur': {'dps.report': None, 'GW2Raidar': None}
        },
        'W2': {
            'Slothasor': {'dps.report': None, 'GW2Raidar': None},
            'Matthias Gabrel': {'dps.report': None, 'GW2Raidar': None}
        },
        'W3': {
            'Keep Construct': {'dps.report': None, 'GW2Raidar': None},
            'Xera': {'dps.report': None, 'GW2Raidar': None}
        },
        'W4': {
            'Cairn the Indomitable': {'dps.report': None, 'GW2Raidar': None},
            'Mursaat Overseer': {'dps.report': None, 'GW2Raidar': None},
            'Samarog': {'dps.report': None, 'GW2Raidar': None},
            'Deimos': {'dps.report': None, 'GW2Raidar': None}
        },
        'W5': {
            'Soulless Horror': {'dps.report': None, 'GW2Raidar': None},
            'Dhuum': {'dps.report': None, 'GW2Raidar': None}
        }
    },
    'fractals': {
        '99CM': {
            'MAMA': {'dps.report': None, 'GW2Raidar': None},
            'Nightmare Oratuss': {'dps.report': None, 'GW2Raidar': None},
            'Ensolyss of the Endless Torment': {'dps.report': None, 'GW2Raidar': None}
        },
        '100CM': {
            'Skorvald the Shattered': {'dps.report': None, 'GW2Raidar': None},
            'Artsariiv': {'dps.report': None, 'GW2Raidar': None},
            'Arkk': {'dps.report': None, 'GW2Raidar': None}
        }
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
        
        for e in logs[type]:
            encount = e + ':'
            await ctx.send(encount)
            for b in logs[type][e]:
                path = 'C:/Users/atl/Documents/Guild Wars 2/addons/arcdps/arcdps.cbtlogs/' + b + '/*'
                all_files = glob.glob(path)
                latest_file = max(all_files, key=os.path.getctime)
                if latest_file is None:
                    logs[type][e][b]['dps.report'] = None
                        
                dps_endpoint = 'https://dps.report/uploadContent?json=1&generator=rh'
                files = {'file': open(latest_file, 'rb')}
                res = requests.post(dps_endpoint, files=files)
                if not res.status_code == 200:
                    logs[type][e][b]['dps.report'] = None
                else:
                    logs[type][e][b]['dps.report'] = res.json()['permalink']
                    
                if logs[type][e][b]['dps.report'] is None:
                    await ctx.send('ERROR 🤖')
                else:
                    await ctx.send(logs[type][e][b]['dps.report'])
        
def setup(bot):
    bot.add_cog(Arcdps(bot))
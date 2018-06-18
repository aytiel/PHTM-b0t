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
        
        for e in logs[type]:
            for b in logs[type][e]:
                path = 'C:/Users/atl/Documents/Guild Wars 2/addons/arcdps/arcdps.cbtlogs/' + b + '/*'
                all_files = glob.glob(path)
                latest_file = max(all_files, key=os.path.getctime)
                if latest_file is None:
                    logs[type][e][b]['dps.report'] = None
                files = {'file': open(latest_file, 'rb')}
                        
                dps_endpoint = 'https://dps.report/uploadContent?json=1&generator=rh'
                res = requests.post(dps_endpoint, files=files)
                if not res.status_code == 200:
                    logs[type][e][b]['dps.report'] = 'ERROR 🤖'
                else:
                    logs[type][e][b]['dps.report'] = res.json()['permalink']
                print('Uploaded ' + b)
                    
        await self.print_logs(ctx, type, name)
                    
                #raidar_endpoint = 'https://www.gw2raidar.com/api/v2/token'
                #cred = {'username': settings.config.RAIDARUSER, 'password': settings.config.RAIDARPASS}
                #res = requests.post(raidar_endpoint, data=cred)
                #if not res.status_code == 200:
                #    logs[type][e][b]['GW2Raidar'] = 'ERROR 🤖'
                #else:
                #    token = res.json()['token']
                #    auth = 'Token ' + token
                #    raidar_endpoint = 'https://www.gw2raidar.com/api/v2/encounters/new'
                #    res = requests.put(raidar_endpoint, headers={'Authorization': auth}, files=files)
                #    print(res)
                #    print(res.text)
                    
    async def print_logs(self, ctx, type: str, name: str):
        title = '__' + name + ' | ' + str(datetime.date.today()) + '__'
        embed = discord.Embed(title=title, colour=0x6496e5)
        embed.set_footer(text='Created by Phantom#4985')
        embed.set_thumbnail(url='https://vignette.wikia.nocookie.net/gwwikia/images/4/4d/Guild_Wars_2_Dragon_logo.jpg/revision/latest?cb=20090825055046')
        for e in logs[type]:
            out = ''
            name = e + ':'
            count = 0
            for b in logs[type][e]:
                boss = b
                if boss == 'Nightmare Oratuss':
                    boss = 'Siax'
                else:
                    split = boss.split(' ')
                    if len(split) > 1:
                        if split[1] == 'the' or split[1] == 'of' or split[1] == 'Gabrel':
                            boss = split[0]
                out += '[' + boss + '](' + logs[type][e][b]['dps.report'] + ')  '
                if not count == len(logs[type][e])-1:
                    out += '|  '
                count += 1
            embed.add_field(name=name, value=out, inline=False)
            
        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Arcdps(bot))